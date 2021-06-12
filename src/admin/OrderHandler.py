import logging
from jsonrpcserver import method, async_dispatch as dispatch
from src.model.Order import Order
from src.model.BaseModel import DBManager
import uuid
from datetime import datetime
from jsonrpcserver.exceptions import ApiError
from src.settings import adminErrorCode


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
        orders = await DBManager.execute(Order.select().where(Order.roomID == roomID))
        invalidRoomID = True
        for order in orders:
            invalidRoomID = False
            if order.state == "using" or order.state == "unpaid":
                raise ApiError("房间不可用", code=40103)
        if invalidRoomID:
            raise ApiError("无效的房间 ID", code=adminErrorCode.CREATE_ORDER_INVALID_ROOM_ID)

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
        fetchOrders [summary]

        Args:
            filter (dict): [description]

        Returns:
            dict: [description]
        """
        userID = filter["userID"] if "userID" in filter else None
        roomID = filter["roomID"] if "roomID" in filter else None
        state = filter["state"] if "state" in filter else None

        logging.info("fetch orders...")
        return {}

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
        return {}
