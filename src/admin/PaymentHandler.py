import logging
from jsonrpcserver import method, async_dispatch as dispatch
from src.settings import adminErrorCode
from jsonrpcserver.exceptions import ApiError
from src.model import *


class PaymentHandler:
    async def run(self, message: str, websocket) -> None:
        response = await dispatch(message)
        if response.wanted:
            await websocket.send(str(response))

    @method
    async def makePayment(orderID: str) -> None:
        # TODO @Jun丶
        """
        makePayment 为账单付款

        Args:
            orderID (str): 订单ID
        """
        logging.info("make payment...")

        result = await DBManager.execute(Order.select().where(Order.orderID == orderID))

        orders = list(result)
        if len(orders) == 0:
            raise ApiError("无效的订单ID", code=adminErrorCode.MAKE_PAYMENT_INVALID_ORDER_ID)
        order = orders[0]
        if order.state != "unpaid":
            raise ApiError(
                "非法的订单状态", code=adminErrorCode.MAKE_PAYMENT_INVALID_ORDER_STATE
            )

        await DBManager.execute(
            Order.update({Order.state: "completed"}).where(Order.orderID == orderID)
        )

        return None
