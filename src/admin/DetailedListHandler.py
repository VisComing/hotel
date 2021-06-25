import logging
import time
from jsonrpcserver import method, async_dispatch as dispatch
from jsonrpcserver.methods import Method
from src.model import *
from src.settings import adminErrorCode
from jsonrpcserver.exceptions import ApiError


class DetailedListHandler:
    async def run(self, message: str, websocket) -> None:
        """
        run jsonrpc将不同的调用指派到不同的函数上
        """
        response = await dispatch(message)
        if response.wanted:
            await websocket.send(str(response))

    @method
    async def getDetailedList(orderID: str) -> dict:
        # TODO @Jun丶
        """
        getDetailedList 获取详单

        Args:
            orderID (str): 订单ID

        Returns:
            dict: {"startTime", "endTime", "windSpeed", "billingRate"}

        """
        logging.info("get detailed list...")

        orders = await DBManager.execute(Order.select().where(Order.orderID == orderID))
        orders = list(orders)
        order = orders[0]
        if len(orders) == 0:
            raise ApiError(
                "无效的订单ID", code=adminErrorCode.GET_DETAILED_LIST_INVALID_ORDER_ID
            )
        if order.state == "using":
            raise ApiError(
                "非法的订单状态", code=adminErrorCode.GET_DETAILED_LIST_INVALID_ORDER_STATE
            )

        detailedlist = await DBManager.execute(
            DetailListItem.select()
            .where(DetailListItem.orderID == orderID)
            .order_by(DetailListItem.startTime)
        )
        dlist = list()
        for items in detailedlist:
            if items.windSpeed == 1:
                windSpeed = "low"
            elif items.windSpeed == 2:
                windSpeed = "medium"
            elif items.windSpeed == 3:
                windSpeed = "high"
            item = {
                "startTime": round(time.mktime(items.startTime.timetuple())),
                "endTime": round(time.mktime(items.endtime.timetuple())),
                "windSpeed": windSpeed,
                "billingRate": items.billingRate,
            }
            dlist.append(item)

        return {"items": dlist}
