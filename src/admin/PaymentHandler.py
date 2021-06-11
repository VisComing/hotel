import logging
from jsonrpcserver import method, async_dispatch as dispatch


class PaymentHandler:
    async def run(self, message: str, websocket) -> None:
        response = await dispatch(message)
        if response.wanted:
            await websocket.send(str(response))

    @method
    async def makePayment(orderID: str):
        pass
