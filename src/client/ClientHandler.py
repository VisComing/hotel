import asyncio
from src.model import *
from datetime import datetime
import math
from jsonrpcclient.clients.websockets_client import WebSocketsClient
import websockets
import logging


class ClientHandler:
    global rooms
    rooms={}

    async def addRoom(self,roomID,web) -> None:
        global rooms

        rooms[roomID]=web
        #print(roomID)
        #print(rooms[roomID])


    async def deleteRoom(self,roomID) -> None:
        global rooms

        rooms.pop(roomID)



    async def run(self) -> None:
        global timeUnit
        global maxSupplyNum             #服务队列最多支持得数量
        global supplyQueue       #roomID,风速,服务时间
        global waitQueue       #roomID,风速,等待次数,等待时间
        global askQueue
        global askWindRoomList       #请求送风的房间ID列表
        global waitTime        #一次等待的时间
        global allRoom
        global sendMessage

        timeUnit=1
        maxSupplyNum=4             
        supplyQueue=[]       
        waitQueue=[]       
        askQueue=[]
        askWindRoomList=[]       
        waitTime=5          
        allRoom=[]
        sendMessage=[]

        await self.schedule()



    #insert into  tbdevice  values('01-01-02',1,25,24,1,1,0,0);
    #建表
    #Device.create_table(True)
    #Scheduling.create_table(True)
    #Order.create_table(True)
    #UsageRecord.create_table(True)


    async def schedule(self) -> None:
        while True:
            await queryDevices()
            await calculate()
            await setFee()

            #预处理
            await preTreat()          

            #将请求队列排序
            await askSort()
            tmp=[]
            for cell in askQueue:
                tmp.append(cell)

            for cell in tmp:
                await scheduleHandler(cell)          #调度算法

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
            await sendFee()
            # print(1)
            #print(rooms)
            await asyncio.sleep(timeUnit)


async def askToSupply(roomID):           #申请队列到服务队列
    for cell in askQueue:
        if(cell[0]==roomID):
            supplyCell=[cell[0],cell[1],0]
            supplyQueue.append(supplyCell)
            askQueue.remove(cell)
    """
    更新调度记录表
    """
    currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await DBManager.create(
            Scheduling, roomID=roomID, timePoint=currentTime
        )
    """
    发送恢复送风信息
    """
    sendRoom=list(rooms.keys())
    result=await DBManager.execute(
        Device.select().where(Device.roomID==roomID)
    )
    speed=result[0].windSpeed
    if roomID in sendRoom:    
        try:
            await WebSocketsClient(rooms[roomID]).notify(
                method_name="WindSupplyResumed", windSpeed=speed
            )
        except websockets.exceptions.ConnectionClosedError as e:
            # 客户端断开连接异常
            logging.warning(e)



async def askToWait(roomID):           #申请队列到等待队列
    for cell in askQueue:
        if(cell[0]==roomID):
            if cell[3]==0:
                waitCell=[cell[0],cell[1],cell[2]+1,waitTime]
                waitQueue.append(waitCell)
                askQueue.remove(cell)
            else:
                waitCell=cell
                waitQueue.append(waitCell)
                askQueue.remove(cell)

    """
    发送停止送风信息
    """
    sendRoom=list(rooms.keys())
    if roomID in sendRoom:    
        try:
            await WebSocketsClient(rooms[roomID]).notify(
                method_name="WindSupplySuspended", reason="scheduling"
            )
        except websockets.exceptions.ConnectionClosedError as e:
            # 客户端断开连接异常
            logging.warning(e)


async def waitToSupply(roomID):           #等待队列到服务队列
    for cell in waitQueue:
        if(cell[0]==roomID):
            supplyCell=[cell[0],cell[1],0]
            supplyQueue.append(supplyCell)
            waitQueue.remove(cell)
    """
    更新调度记录表
    """
    currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await DBManager.create(
            Scheduling, roomID=roomID, timePoint=currentTime
        )
    """
    发送恢复送风信息
    """
    sendRoom=list(rooms.keys())
    result=await DBManager.execute(
        Device.select().where(Device.roomID==roomID)
    )
    speed=result[0].windSpeed
    if roomID in sendRoom:    
        try:
            await WebSocketsClient(rooms[roomID]).notify(
                method_name="WindSupplyResumed", windSpeed=speed
            )
        except websockets.exceptions.ConnectionClosedError as e:
            # 客户端断开连接异常
            logging.warning(e)


async def supplyToWait(roomID):           #服务队列到等待队列
    for cell in supplyQueue:
        if(cell[0]==roomID):
            waitCell=[cell[0],cell[1],1,waitTime]
            waitQueue.append(waitCell)
            supplyQueue.remove(cell)

    """
    发送停止送风信息
    """
    sendRoom=list(rooms.keys())
    if roomID in sendRoom:    
        try:
            await WebSocketsClient(rooms[roomID]).notify(
                method_name="WindSupplySuspended", reason="scheduling"
            )
        except websockets.exceptions.ConnectionClosedError as e:
            # 客户端断开连接异常
            logging.warning(e)


async def delectRoom(roomID):             #删除某停止请求送风的房间
    for cell in waitQueue:
        if(cell[0]==roomID):
            waitQueue.remove(cell)
    for cell in supplyQueue:
        if(cell[0]==roomID):
            supplyQueue.remove(cell)


async def swap(x,y):
    tmp=['x',0,0,0]
    for i in range(0,4):
        tmp[i]=x[i]
        x[i]=y[i]
        y[i]=tmp[i]


async def askSort():           #按照风速和等待次数排序
    n=len(askQueue)
    for i in range(0,n-1):
        for j in range(0,n-1-i):
            if askQueue[j][1] < askQueue[j+1][1]:            
                await swap(askQueue[j],askQueue[j+1])
            elif askQueue[j][1] == askQueue[j+1][1] and askQueue[j][2] < askQueue[j+1][2]:
                await swap(askQueue[j],askQueue[j+1])
            elif askQueue[j][1] == askQueue[j+1][1] and askQueue[j][2] == askQueue[j+1][2] and askQueue[j][3] > askQueue[j+1][3]:
                await swap(askQueue[j],askQueue[j+1])



async def queryDevices():
    global allRoom

    allRoom=[]
    result=await DBManager.execute(
        Device.select()
    )
    for cell in result:
        allRoom.append([cell.roomID,cell.windSpeed,cell.isAskAir,cell.isSupplyAir,
                        cell.cost,cell.supplyTime])
    #print(allRoom)


async def calculate():
    global allRoom
    global sendMessage

    sendMessage=[]
    for cell in allRoom:
        if cell[3]==False:
            billingRate=0
        elif cell[1]==1:
            billingRate=1/180
        elif cell[1]==2:
            billingRate=1/120
        else:
            billingRate=1/60
        cost=cell[4]+billingRate*timeUnit
        if cell[3]==True:
            supplyTime=cell[5]+timeUnit
        else:
            supplyTime=cell[5]
        sendMessage.append([cell[0],cell[1],billingRate,cost,supplyTime])
    #print(sendMessage)


async def setFee():
    global sendMessage

    for cell in sendMessage:
        await DBManager.execute(
                Device.update(cost=cell[3],supplyTime=cell[4]).where(Device.roomID == cell[0])
        )
    for cell in sendMessage:
        currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        result=await DBManager.execute(
            Order.select().where(Order.roomID == cell[0] , Order.state=='using')
        )
        theOrder=result[0].orderID
        #print(theOrder)
        result=await DBManager.execute(
            UsageRecord.select().where(UsageRecord.orderID == theOrder , UsageRecord.startTime==UsageRecord.endTime)
        )
        if len(result)==0:
            await DBManager.create(
            UsageRecord, orderID=theOrder, startTime=currentTime , endTime=currentTime,
                            windSpeed=cell[1], cost=cell[3] , billingRate=cell[2]
        )
        else:
            check=math.isclose(result[0].billingRate, cell[2], rel_tol=1e-04)
            if check==False:
                await DBManager.execute(
                    UsageRecord.update(endTime=currentTime).where(UsageRecord.orderID == theOrder)
                )
                await DBManager.create(
                    UsageRecord, orderID=theOrder, startTime=currentTime , endTime=currentTime,
                                    windSpeed=cell[1], cost=cell[3] , billingRate=cell[2]
                )



async def sendFee():
    global sendMessage

    sendRoom=list(rooms.keys())
    for cell in sendMessage:
        if cell[0] in sendRoom:    
            try:
                await WebSocketsClient(rooms[cell[0]]).notify(
                    method_name="BillingInformationUpdate", billingRate=cell[2],
                                                                    totalCost=cell[3],
                                                                    totalServiceTime=cell[4]
                )
            except websockets.exceptions.ConnectionClosedError as e:
                # 客户端断开连接异常
                logging.warning(e)




async def preTreat():          #调度算法前预处理

    #服务时间+1
    for i in range(0,len(supplyQueue)):
        supplyQueue[i][2]=supplyQueue[i][2]+1

    #等待时间-1
    for i in range(0,len(waitQueue)):
        waitQueue[i][3]=waitQueue[i][3]-1
    
    """
    通过device表获取所有停止请求送风的roomID，isAskAir=false
    并将device中所有停止请求送风的isSupplyAir置为false
    """
    stopWindRoomID=[]
    result=await DBManager.execute(
        Device.select().where(Device.isAskAir == False)
    )
    for cell in result:
        stopWindRoomID.append(cell.roomID)

    await DBManager.execute(
        Device.update(isSupplyAir=False).where(Device.isAskAir == False)
    )
    """
    发送停止送风信息
    """
    sendRoom=list(rooms.keys())
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
    askWindRoomID=[]
    result=await DBManager.execute(
        Device.select().where(Device.isAskAir == True)
    )
    for cell in result:
        askWindRoomID.append([cell.roomID,cell.windSpeed])

    #删除已停止请求送风的房间ID
    for i in range(0,len(stopWindRoomID)):
        if(stopWindRoomID[i] in askWindRoomList):
            await delectRoom(stopWindRoomID[i])
            askWindRoomList.remove(stopWindRoomID[i])

    #更新风速
    for cell in askWindRoomID:
        await updateSpeed(cell)


    #构建请求队列
    for i in range(0,len(askWindRoomID)):
        if(askWindRoomID[i][0] not in askWindRoomList):
            askQueue.append([askWindRoomID[i][0],askWindRoomID[i][1],0,0])
            askWindRoomList.append(askWindRoomID[i][0])
    for cell in waitQueue:
        askQueue.append(cell)
        waitQueue.remove(cell)

    #print(askQueue)


async def updateSpeed(askRoom):
    for cell in supplyQueue:
        if cell[0]==askRoom[0]:
            cell[1]=askRoom[1]
    for cell in waitQueue:
        if cell[0]==askRoom[0]:
            cell[1]=askRoom[1]


async def windJudge(room):
    min=4
    for cell in supplyQueue:
        if cell[1]<min:
            min=cell[1]
    if room[1]<min:
        return -1
    elif room[1]==min:
        return 0
    else:
        return min         #返回最小风速


async def findMaxSRoom(speed):            #找到特定风速下最大服务时间的房间ID
    
    maxRoomID=''
    maxSupplyTime=-1
    for cell in supplyQueue:
        if cell[1]==speed:
            if cell[2]>maxSupplyTime:
                maxRoomID=cell[0]
                maxSupplyTime=cell[2]
    return maxRoomID


async def scheduleHandler(room):          #调度算法
    
    #调度队列未满
    if len(supplyQueue)<maxSupplyNum:
        await askToSupply(room[0])
    #调度队列已满
    elif room[3]!=0:
        await askToWait(room[0])
    else:
        check=await windJudge(room)

        #判断是否符合优先级策略,如果判断为大于
        if check>0:
            maxRoomID=await findMaxSRoom(check)
            if maxRoomID!='':
                await supplyToWait(maxRoomID)
                await askToSupply(room[0])

        #如果判断为相等
        elif check==0:
            #若waitNum=0
            if room[2]==0:
                await askToWait(room[0])
            #若waitNum>0
            else:
                maxRoomID=await findMaxSRoom(room[1])
                if maxRoomID!='':
                    await supplyToWait(maxRoomID)
                    await askToSupply(room[0])

        #如果判断为小于
        else:
            await askToWait(room[0])



