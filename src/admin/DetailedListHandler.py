from jsonrpcserver import method, async_dispatch as dispatch
from jsonrpcserver.methods import Method


class DetailedListHandler:
    async def run(self):
        await dispatch(self._message)

    @method
    async def getDetailedList(orderID: str):
        pass
