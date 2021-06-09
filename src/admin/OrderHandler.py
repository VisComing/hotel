import logging
from jsonrpcserver import method, async_dispatch as dispatch


class OrderHandler:
    def __init__(self, message) -> None:
        self._message = message

    async def run(self):
        await dispatch(self._message)

    @method
    async def createOrder(userID: str, roomID: str):
        logging.info("create order...")
        pass

    @method
    async def fetchOrders(filter: dict):
        userID = filter["userID"] if "userID" in filter else None
        roomID = filter["roomID"] if "roomID" in filter else None
        state = filter["state"] if "state" in filter else None

        logging.info("fetch orders...")
        pass

    @method
    async def finishOrder(orderID: str):
        logging.info("finish order...")
        pass
