import logging
from jsonrpcserver import method, async_dispatch as dispatch


class OrderHandler:
    async def run(self, message):
        await dispatch(message)

    @method
    async def createOrder(userID: str, roomID: str):
        logging.info("create order...")
        return {"roomID": "zhou_rui_fa"}

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
