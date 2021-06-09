import logging
from jsonrpcserver import method, async_dispatch as dispatch


class BillHandler:
    def __init__(self, message) -> None:
        self._message = message

    async def run(self):
        await dispatch(self._message)

    @method
    async def getBill(orderID: str):
        pass
