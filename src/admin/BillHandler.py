import logging
from jsonrpcserver import method, async_dispatch as dispatch


class BillHandler:
    async def run(self) -> None:
        await dispatch(self._message)

    @method
    async def getBill(orderID: str) -> dict:
        return {"orderID": "123", "billID": "123", "totalCost": "123"}
