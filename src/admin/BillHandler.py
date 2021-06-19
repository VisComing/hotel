import logging
from jsonrpcserver.exceptions import ApiError

from peewee_async import select
from src.model.BaseModel import DBManager
from jsonrpcserver import method, async_dispatch as dispatch
from src.model import *
from src.settings import adminErrorCode


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
            dict: {"orderID", "billID", "totalCost"}
        """

        logging.info("get bill...")

        orders = await DBManager.execute(Order.select().where(Order.orderID == orderID))
        orders = list(orders)
        if len(orders) == 0:
            raise ApiError("无效的订单ID", code=adminErrorCode.GET_BILL_INVALID_ORDER_ID)
        order = orders[0]
        if order.state == "using":
            raise ApiError("非法的订单状态", code=adminErrorCode.GET_BILL_INVALID_ORDER_STATE)

        bills = await DBManager.execute(Bill.select().where(Bill.orderID == orderID))
        bills = list(bills)
        bill = bills[0]

        return {"orderID": orderID, "billID": bill.billID, "totalCost": bill.totalCost}
