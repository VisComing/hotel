import asyncio
from src.model import *
from datetime import datetime
import math
from jsonrpcclient.clients.websockets_client import WebSocketsClient
import websockets
import logging


# ClientHandler类
class ClientHandler:
    global rooms
    rooms = {}

    # 构建字典，建立房间号与连接的关系
    # 输入房间号、连接
    # 无输出
    async def addRoom(self, roomID, web) -> None:
        global rooms
        rooms[roomID] = web

    # 删除字典，解除房间号与连接的关系
    # 输入房间号
    # 无输出
    async def deleteRoomByID(self, roomID) -> None:
        global rooms
        rooms.pop(roomID)

    # 删除字典，解除房间号与连接的关系
    # 输入websocket
    # 无输出
    async def deleteRoomByWeb(self, websocket) -> None:
        # 获取存在连接的房间
        sendRoom = list(rooms.keys())
        for roomID in sendRoom:
            if rooms[roomID] == websocket:
                rooms.pop(roomID)

    # 开始执行
    # 无输入
    # 无输出
    async def run(self) -> None:
        global supplyQueue  # 服务队列：roomID,风速,服务时间
        global waitQueue  # 等待队列：roomID,风速,等待次数,等待时间
        global askQueue  # 请求队列：roomID,风速,等待次数,等待时间
        global askWindRoomList  # 请求送风的房间ID列表

        supplyQueue = []
        waitQueue = []
        askQueue = []
        askWindRoomList = []
        timeUnit = 1
        waitTime = 5

        """
        获取配置信息
        """
        result = await DBManager.execute(Settings.select())
        # 相关配置信息
        maxSupplyNum = result[0].maxNumOfClientsToServe
        electricityPrice = result[0].electricityPrice
        rateing = {
            "low": result[0].lowRate * electricityPrice / 60,
            "mid": result[0].midRate * electricityPrice / 60,
            "high": result[0].highRate * electricityPrice / 60,
        }

        # 开始循环
        await self.schedule(maxSupplyNum, waitTime, rateing, timeUnit)

    # 定时发送计费信息和调度
    # 输入 maxSupplyNum（最大调度数）,waitTime(等待队列一次等待时间),rateing(计费速率参数),timeUnit（多久循环一次）
    # 无输出
    async def schedule(self, maxSupplyNum, waitTime, rateing, timeUnit) -> None:
        while True:

            # 调度前发送计费信息等
            await sendBillingMessage(rateing, timeUnit)

            # 预处理
            await preTreat()

            # 将请求队列排序
            await askSort()

            # 构建请求队列
            tmp = []
            for cell in askQueue:
                tmp.append(cell)

            for cell in tmp:
                await scheduleHandler(cell, maxSupplyNum, waitTime)  # 调度算法

            """
            更新device表，将所有supplyQueue中的roomID的isSupplyAir置为true
            更新device表，将所有waitQueue中的roomID的isSupplyAir置为false
            """
            for cell in supplyQueue:
                await DBManager.execute(
                    Device.update(isSupplyAir=True).where(Device.roomID == cell[0])
                )
            for cell in waitQueue:
                await DBManager.execute(
                    Device.update(isSupplyAir=False).where(Device.roomID == cell[0])
                )

            await asyncio.sleep(timeUnit)


# 调度前发送计费信息等
# 输入 rateing(计费速率参数),timeUnit（多久循环一次）
# 输出 无
async def sendBillingMessage(rateing, timeUnit):

    # 查询所有存在使用订单的房间号
    allRoom = await queryDevices()
    if allRoom != None:
        # 计算 billingRate,cost,supplyTime，并更新device表，UsageRecord表，发送计费信息
        await calculate(allRoom, rateing, timeUnit)


# 查询所有存在使用订单的房间号
# 输入 无
# 返回 房间状态字典列表或None
async def queryDevices():

    allRoom = []
    # 查询存在using订单的房间号
    result = await DBManager.execute(Order.select().where(Order.state == "using"))
    # 若存在using订单的房间，查询device表中该房间的相关信息
    if len(result) != 0:
        for cell in result:
            roomState = await DBManager.execute(
                Device.select().where(Device.roomID == cell.roomID)
            )
            allRoom.append(roomState[0])
        return allRoom
    # 若不存在using订单的房间，返回空
    else:
        return None


# 计算 billingRate,cost,supplyTime，并更新device表，UsageRecord表，发送计费信息
# 输入 所有存在使用订单的房间字典,rateing(计费速率参数),timeUnit（多久循环一次）
# 返回待发送的计费信息
async def calculate(allRoom, rateing, timeUnit):

    for cell in allRoom:
        if cell.isSupplyAir == False:
            billingRate = 0
        elif cell.windSpeed == 1:
            billingRate = rateing["low"]
        elif cell.windSpeed == 2:
            billingRate = rateing["mid"]
        else:
            billingRate = rateing["high"]
        theCost = cell.cost + billingRate * timeUnit
        if cell.isSupplyAir == True:
            theSupplyTime = cell.supplyTime + timeUnit
        else:
            theSupplyTime = cell.supplyTime

        # 更新device表
        await DBManager.execute(
            Device.update(cost=theCost, supplyTime=theSupplyTime).where(
                Device.roomID == cell.roomID
            )
        )
        # 更新或生成UsageRecord表（使用记录）
        await createUsageRecord(
            cell.roomID, cell.windSpeed, billingRate, theCost, theSupplyTime
        )
        # 发送计费信息
        await sendFee(cell.roomID, billingRate, theCost, theSupplyTime)


# 更新或生成UsageRecord表
# 输入 roomID,windSpeed,billingRate,theCost,theSupplyTime
# 返回 无
async def createUsageRecord(roomID, theWindSpeed, billingRate, theCost, theSupplyTime):

    # 当前时间
    currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 查询是否此房间存在使用状态的订单
    result = await DBManager.execute(
        Order.select().where(Order.roomID == roomID, Order.state == "using")
    )
    theOrder = result[0].orderID

    # 查询此条使用记录是否已被创建
    result = await DBManager.execute(
        UsageRecord.select().where(
            UsageRecord.orderID == theOrder,
            UsageRecord.startTime == UsageRecord.endTime,
        )
    )

    # 无使用记录，创建使用记录
    if len(result) == 0:
        await DBManager.create(
            UsageRecord,
            orderID=theOrder,
            startTime=currentTime,
            endTime=currentTime,
            windSpeed=theWindSpeed,
            cost=theCost,
            billingRate=billingRate,
        )
    # 存在使用记录，更新endTime
    else:
        # 判断是否存在费率更新
        check = math.isclose(result[0].billingRate, billingRate, rel_tol=1e-04)
        # 存在更新
        if check == False:
            # 更新endTime
            await DBManager.execute(
                UsageRecord.update(endTime=currentTime).where(
                    UsageRecord.orderID == theOrder
                )
            )
            # 创建新的使用记录
            await DBManager.create(
                UsageRecord,
                orderID=theOrder,
                startTime=currentTime,
                endTime=currentTime,
                windSpeed=theWindSpeed,
                cost=theCost,
                billingRate=billingRate,
            )


# 发送计费信息
# 输入 roomID,billingRate,theCost,theSupplyTime
# 输出 无
async def sendFee(roomID, billingRate, theCost, theSupplyTime):

    # 获取存在连接的房间
    sendRoom = list(rooms.keys())

    # 房间存在连接
    if roomID in sendRoom:
        try:
            await WebSocketsClient(rooms[roomID]).notify(
                method_name="BillingInformationUpdate",
                billingRate=billingRate,
                totalCost=theCost,
                totalServiceTime=theSupplyTime,
            )
        except websockets.exceptions.ConnectionClosedError as e:
            # 客户端断开连接异常
            logging.warning(e)


# 申请队列到服务队列
async def askToSupply(roomID):

    speedList=["","low","medium","high"]

    for cell in askQueue:
        if cell[0] == roomID:
            supplyCell = [cell[0], cell[1], 0]
            supplyQueue.append(supplyCell)
            askQueue.remove(cell)
    """
    更新调度记录表
    """
    currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await DBManager.create(Scheduling, roomID=roomID, timePoint=currentTime)
    """
    发送恢复送风信息
    """
    sendRoom = list(rooms.keys())
    result = await DBManager.execute(Device.select().where(Device.roomID == roomID))
    speed = result[0].windSpeed
    if roomID in sendRoom:
        try:
            await WebSocketsClient(rooms[roomID]).notify(
                method_name="WindSupplyResumed", windSpeed=speedList[speed]
            )
        except websockets.exceptions.ConnectionClosedError as e:
            # 客户端断开连接异常
            logging.warning(e)


# 申请队列到等待队列
async def askToWait(roomID, waitTime):
    for cell in askQueue:
        if cell[0] == roomID:
            if cell[3] == 0:
                waitCell = [cell[0], cell[1], cell[2] + 1, waitTime]
                waitQueue.append(waitCell)
                askQueue.remove(cell)
            else:
                waitCell = cell
                waitQueue.append(waitCell)
                askQueue.remove(cell)

    """
    发送停止送风信息
    """
    sendRoom = list(rooms.keys())
    if roomID in sendRoom:
        try:
            await WebSocketsClient(rooms[roomID]).notify(
                method_name="WindSupplySuspended", reason="scheduling"
            )
        except websockets.exceptions.ConnectionClosedError as e:
            # 客户端断开连接异常
            logging.warning(e)


# 等待队列到服务队列
async def waitToSupply(roomID):

    speedList=["","low","medium","high"]

    for cell in waitQueue:
        if cell[0] == roomID:
            supplyCell = [cell[0], cell[1], 0]
            supplyQueue.append(supplyCell)
            waitQueue.remove(cell)
    """
    更新调度记录表
    """
    currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await DBManager.create(Scheduling, roomID=roomID, timePoint=currentTime)
    """
    发送恢复送风信息
    """
    sendRoom = list(rooms.keys())
    result = await DBManager.execute(Device.select().where(Device.roomID == roomID))
    speed = result[0].windSpeed
    if roomID in sendRoom:
        try:
            await WebSocketsClient(rooms[roomID]).notify(
                method_name="WindSupplyResumed", windSpeed=speedList[speed]
            )
        except websockets.exceptions.ConnectionClosedError as e:
            # 客户端断开连接异常
            logging.warning(e)


# 服务队列到等待队列
async def supplyToWait(roomID, waitTime):
    for cell in supplyQueue:
        if cell[0] == roomID:
            waitCell = [cell[0], cell[1], 1, waitTime]
            waitQueue.append(waitCell)
            supplyQueue.remove(cell)

    """
    发送停止送风信息
    """
    sendRoom = list(rooms.keys())
    if roomID in sendRoom:
        try:
            await WebSocketsClient(rooms[roomID]).notify(
                method_name="WindSupplySuspended", reason="scheduling"
            )
        except websockets.exceptions.ConnectionClosedError as e:
            # 客户端断开连接异常
            logging.warning(e)


# 删除某停止请求送风的房间
# 输入 房间ID
# 输出 无
async def delectRoom(roomID):
    for cell in waitQueue:
        if cell[0] == roomID:
            waitQueue.remove(cell)
    for cell in supplyQueue:
        if cell[0] == roomID:
            supplyQueue.remove(cell)


# 交换两房间ID位置
async def swap(x, y):
    tmp = ["x", 0, 0, 0]
    for i in range(0, 4):
        tmp[i] = x[i]
        x[i] = y[i]
        y[i] = tmp[i]


# 按照风速和等待次数排序
async def askSort():
    n = len(askQueue)
    for i in range(0, n - 1):
        for j in range(0, n - 1 - i):
            if askQueue[j][1] < askQueue[j + 1][1]:
                await swap(askQueue[j], askQueue[j + 1])
            elif (
                askQueue[j][1] == askQueue[j + 1][1]
                and askQueue[j][2] < askQueue[j + 1][2]
            ):
                await swap(askQueue[j], askQueue[j + 1])
            elif (
                askQueue[j][1] == askQueue[j + 1][1]
                and askQueue[j][2] == askQueue[j + 1][2]
                and askQueue[j][3] > askQueue[j + 1][3]
            ):
                await swap(askQueue[j], askQueue[j + 1])


# 调度算法前预处理
async def preTreat():

    # 服务时间+1
    for i in range(0, len(supplyQueue)):
        supplyQueue[i][2] = supplyQueue[i][2] + 1

    # 等待时间-1
    for i in range(0, len(waitQueue)):
        waitQueue[i][3] = waitQueue[i][3] - 1

    """
    通过device表获取所有停止请求送风的roomID，isAskAir=false
    并将device中所有停止请求送风的isSupplyAir置为false
    """
    stopWindRoomID = []
    result = await DBManager.execute(Device.select().where(Device.isAskAir == False))
    for cell in result:
        stopWindRoomID.append(cell.roomID)

    await DBManager.execute(
        Device.update(isSupplyAir=False).where(Device.isAskAir == False)
    )
    """
    发送停止送风信息
    """
    sendRoom = list(rooms.keys())
    for roomID in stopWindRoomID:
        if roomID in sendRoom:
            try:
                await WebSocketsClient(rooms[roomID]).notify(
                    method_name="WindSupplySuspended", reason="client-requested"
                )
            except websockets.exceptions.ConnectionClosedError as e:
                # 客户端断开连接异常
                logging.warning(e)

    """
    通过device表获取所有请求送风的roomID和风速，isAskAir=true
    """
    askWindRoomID = []
    result = await DBManager.execute(Device.select().where(Device.isAskAir == True))
    for cell in result:
        askWindRoomID.append([cell.roomID, cell.windSpeed])

    # 删除已停止请求送风的房间ID
    for i in range(0, len(stopWindRoomID)):
        if stopWindRoomID[i] in askWindRoomList:
            await delectRoom(stopWindRoomID[i])
            askWindRoomList.remove(stopWindRoomID[i])

    # 更新风速
    for cell in askWindRoomID:
        await updateSpeed(cell)

    # 构建请求队列
    for i in range(0, len(askWindRoomID)):
        if askWindRoomID[i][0] not in askWindRoomList:
            askQueue.append([askWindRoomID[i][0], askWindRoomID[i][1], 0, 0])
            askWindRoomList.append(askWindRoomID[i][0])
    for cell in waitQueue:
        askQueue.append(cell)
        waitQueue.remove(cell)

    # print(askQueue)


# 更新服务队列和等待队列的风速
# 输入 房间信息
# 无输出
async def updateSpeed(askRoom):
    for cell in supplyQueue:
        if cell[0] == askRoom[0]:
            cell[1] = askRoom[1]
    for cell in waitQueue:
        if cell[0] == askRoom[0]:
            cell[1] = askRoom[1]


# 判断是否符合优先级策略
# 输入 房间信息
# 输出 服务队列的最小风速，若没有，则返回0
async def windJudge(room):
    min = 4
    for cell in supplyQueue:
        if cell[1] < min:
            min = cell[1]
    if room[1] < min:
        return -1
    elif room[1] == min:
        return 0
    else:
        return min  # 返回最小风速


# 找到特定风速下最大服务时间的房间ID
# 输入 房间信息
# 输出 房间ID
async def findMaxSRoom(speed):

    maxRoomID = ""
    maxSupplyTime = -1
    for cell in supplyQueue:
        if cell[1] == speed:
            if cell[2] > maxSupplyTime:
                maxRoomID = cell[0]
                maxSupplyTime = cell[2]
    return maxRoomID


# 调度算法
# 输入 room,maxSupplyNum,waitTime
# 输出 无
async def scheduleHandler(room, maxSupplyNum, waitTime):

    # 调度队列未满
    if len(supplyQueue) < maxSupplyNum:
        await askToSupply(room[0])
    # 调度队列已满
    elif room[3] != 0:
        await askToWait(room[0], waitTime)
    else:
        check = await windJudge(room)

        # 判断是否符合优先级策略,如果判断为大于
        if check > 0:
            maxRoomID = await findMaxSRoom(check)
            if maxRoomID != "":
                await supplyToWait(maxRoomID, waitTime)
                await askToSupply(room[0])

        # 如果判断为相等
        elif check == 0:
            # 若waitNum=0
            if room[2] == 0:
                await askToWait(room[0], waitTime)
            # 若waitNum>0
            else:
                maxRoomID = await findMaxSRoom(room[1])
                if maxRoomID != "":
                    await supplyToWait(maxRoomID, waitTime)
                    await askToSupply(room[0])

        # 如果判断为小于
        else:
            await askToWait(room[0], waitTime)
