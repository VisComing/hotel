from jsonrpcserver import method, async_dispatch as dispatch
from jsonrpcserver.methods import Method


class DetailedListHandler:
    async def run(self) -> None:
        """
        run jsonrpc将不同的调用指派到不同的函数上
        """
        await dispatch(self._message)

    @method
    async def getDetailedList(orderID: str) -> dict:
        """
        getDetailedList 获取详单

        Args:
            orderID (str): 订单ID

        Returns:
            dict

        """
        return {}
