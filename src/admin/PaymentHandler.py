import logging
from jsonrpcserver import method, async_dispatch as dispatch


class PaymentHandler:
    async def run(self, message: str) -> None:
        await dispatch(message)

    @method
    async def makePayment(orderID: str):
        pass
