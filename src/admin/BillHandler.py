import logging
from jsonrpcserver import method, async_dispatch as dispatch


class BillHandler:
    async def run(self, message: str, websocket) -> None:
        response = await dispatch(message)
        if response.wanted:
            await websocket.send(str(response))

    @method
    async def getBill(orderID: str) -> dict:
        return {"orderID": "123", "billID": "123", "totalCost": "123"}
