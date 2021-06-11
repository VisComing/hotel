import logging
from jsonrpcserver import method, async_dispatch as dispatch
from src.model.Order import Order


class OrderHandler:
    async def run(self, message: str) -> None:
        """
        run 使用jsonrpc将消息分派给不同函数

        Args:
            message (str): 收到的消息
        """
        await dispatch(message)

    @method
    async def createOrder(userID: str, roomID: str) -> dict:
        """
        createOrder 创建订单

        Args:
            userID (str): [description]
            roomID (str): [description]

        Returns:
            dict: [description]
            #请处理此函数的负责人根据协议填写函数注释以及函数
        """
        logging.info("create order...")
        return {"roomID": "zhou_rui_fa"}

    @method
    async def fetchOrders(filter: dict) -> dict:
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
        """
        finishOrder [summary]

        Args:
            orderID (str): [description]

        Returns:
            dict: [description]
        """
        logging.info("finish order...")
        return {}
