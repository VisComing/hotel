import logging
from jsonrpcserver import method, async_dispatch as dispatch
from src.model.Order import Order


class OrderHandler:
    async def run(self, message) -> None:
        await dispatch(message)

    @method
    async def createOrder(userID: str, roomID: str) -> dict:
        logging.info("create order...")
        return {"roomID": "zhou_rui_fa"}

    @method
    async def fetchOrders(filter: dict) -> dict:
        userID = filter["userID"] if "userID" in filter else None
        roomID = filter["roomID"] if "roomID" in filter else None
        state = filter["state"] if "state" in filter else None

        logging.info("fetch orders...")
        return {}

    @method
    async def finishOrder(orderID: str) -> dict:
        logging.info("finish order...")
        return {}
