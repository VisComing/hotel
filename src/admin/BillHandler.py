import logging
from jsonrpcserver import method, async_dispatch as dispatch


class BillHandler:
    async def run(self):
        await dispatch(self._message)

    @method
    async def getBill(orderID: str):
        pass
