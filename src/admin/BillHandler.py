import logging
from jsonrpcserver import method, async_dispatch as dispatch


class BillHandler:
    async def run(self, message: str, websocket) -> None:
        response = await dispatch(message)
        if response.wanted:
            await websocket.send(str(response))

    @method
    async def getBill(orderID: str) -> dict:
        # TODO @Jun丶
        """
        getBill 获取账单

        Args:
            orderID (str): 订单ID

        Returns:
            dict: 返回值请参考协议
        """
        return {"orderID": "123", "billID": "123", "totalCost": "123"}
