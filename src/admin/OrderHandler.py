import logging
from os import stat
from jsonrpcserver import method, async_dispatch as dispatch
import uuid
from datetime import datetime
from jsonrpcserver.exceptions import ApiError
from src.settings import adminErrorCode
from src.model import *
import time


class OrderHandler:
    async def run(self, message: str, websocket) -> None:
        """
        run 使用jsonrpc将消息分派给不同函数

        Args:
            message (str): 收到的消息
        """
        response = await dispatch(message)
        if response.wanted:
            await websocket.send(str(response))

    @method
    async def createOrder(userID: str, roomID: str) -> dict:
        # TODO @adslppp
        """
        createOrder 创建订单

        Args:
            userID (str): 用户ID
            roomID (str): 房间ID, 格式 01-23-45

        Returns:
            dict: {"orderID":'uuid'}
        """
        room = await DBManager.execute(Device.select().where(Device.roomID == roomID))
        if len(room) == 0:
            raise ApiError("无效的房间 ID", code=adminErrorCode.CREATE_ORDER_INVALID_ROOM_ID)

        orders = await DBManager.execute(
            Order.select().where((Order.roomID == roomID) & (Order.state == "using"))
        )
        if len(orders) > 0:
            raise ApiError("房间不可用", code=adminErrorCode.CREATE_ORDER_ROOM_UNAVAILABLE)

        orderID = str(uuid.uuid1())
        await DBManager.create(
            Order,
            userID=userID,
            roomID=roomID,
            orderID=orderID,
            createdTime=datetime.now(),
            finishedTime=datetime.now(),
            state="using",
        )

        return {"orderID": orderID}

    @method
    async def fetchOrders(filter: dict) -> dict:
        # TODO @Jun丶
        """
        fetchOrders 获取订单列表

        Args:
            filter (obj): 过滤条件
                userID (str): 用户ID
                roomID (str): 房间ID
                state (str): 订单状态 (`using` 代表「使用中」，`unpaid` 代表「未付款」，`completed` 代表「已完成」)

        Returns:
            dict: {"orderID", "userID", "roomID", "createdTime", "finishedTime", "state"}
        """
        userID = filter["userID"] if "userID" in filter else None
        roomID = filter["roomID"] if "roomID" in filter else None
        state = filter["state"] if "state" in filter else None

        logging.info("fetch orders...")

        condition = True
        if userID:
            condition = condition & (Order.userID == userID)
        if roomID:
            condition = condition & (Order.roomID == roomID)
        if state:
            condition = condition & (Order.state == state)
        orders = await DBManager.execute(Order.select().where(condition))
        ods = []
        for order in orders:
            od = {
                "orderID": order.orderID,
                "userID": order.userID,
                "roomID": order.roomID.roomID,
                "createdTime": round(time.mktime(order.createdTime.timetuple())),
                "finishedTime": round(time.mktime(order.finishedTime.timetuple())),
                "state": order.state,
            }
            ods.append(od)

        return {"orders": ods}

    @method
    async def finishOrder(orderID: str) -> dict:
        # TODO @Jun丶
        """
        finishOrder [summary]

        Args:
            orderID (str): [description]

        Returns:
            dict: [description]
        """
        logging.info("finish order...")

        result = await DBManager.execute(Order.select().where(Order.orderID == orderID))

        orders = list(result)
        if len(orders) == 0:
            raise ApiError("无效的订单ID", code=adminErrorCode.FINISH_ORDER_INVALID_ORDER_ID)

        order = orders[0]
        if order.state != "using":
            raise ApiError(
                "非法的订单状态", code=adminErrorCode.FINISH_ORDER_INVALID_ORDER_STATE
            )

        # 修改订单状态和完成时间
        await DBManager.execute(
            Order.update({Order.state: "unpaid"}).where(Order.orderID == orderID)
        )
        await DBManager.execute(
            Order.update({Order.finishedTime: datetime.now()}).where(
                Order.orderID == orderID
            )
        )

        # 将使用记录内的数据存入详单
        totalCost = 0.0
        records = await DBManager.execute(
            UsageRecord.select().where(UsageRecord.orderID == orderID)
        )
        for record in records:
            await DBManager.create(
                DetailListItem,
                orderID=record.orderID.orderID,
                detailListID=str(uuid.uuid1()),
                startTime=record.startTime,
                endtime=record.endTime,
                windSpeed=record.windSpeed,
                cost=record.cost,
                billingRate=record.billingRate,
            )
            # 计算总费用
            totalCost += record.cost

        # 插入一条账单
        billID = str(uuid.uuid1())
        await DBManager.create(
            Bill,
            orderID=orderID,
            billID=billID,
            totalCost=totalCost,
        )

        # 将order对应的room状态修改为缺省值
        # 获取到该订单对应的房间号
        roomOrder = await DBManager.execute(
            Order.select().where(Order.orderID == orderID)
        )
        roomOrder = list(roomOrder)
        roomOrder = roomOrder[0]

        # 获取缺省温度
        settings = await DBManager.execute(Settings.select())
        settings = list(settings)
        settings = settings[0]

        await DBManager.execute(
            Device.update(
                isPower=False,
                targetTemperature=settings.defaultTemperature,
                currentTemperature=settings.defaultTemperature,
                windSpeed=1,
                isAskAir=False,
                isSupplyAir=False,
                cost=0,
                supplyTime=0,
            ).where(Device.roomID == roomOrder.roomID.roomID)
        )
        return None
