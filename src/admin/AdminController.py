import logging
from .OrderHandler import OrderHandler
from .BillHandler import BillHandler
from .DetailedListHandler import DetailedListHandler
from .StatisticsHandler import StatisticsHandler
from .SystemStatusHandler import SystemStatusHandler
import websockets
import json


class AdminController:
    async def control(self, websocket, path):
        async for message in websocket:
            method = json.loads(message)["method"]
            if (
                method == "createOrder"
                or method == "fetchOrders"
                or method == "finishOrder"
            ):
                await self.__setOrderHandler(message)
            elif method == "getBill":
                await self.__setBillHandler(message)
            elif method == "getDetailedList":
                await self.__setDetailedListHandler(message)
            elif method == "getStatistics":
                await self.__setStatisticsHandler(message)
            elif (
                method == "getSystemStatus"
                or method == "startSystem"
                or method == "stopSystem"
            ):
                await self.__setSystemStatusHandler(message)
            elif method == "getSysConfig" or method == "setSysConfig":
                await self.__setSysConfigHandler(message)
            else:
                logging.error("AdminController: rpc failed, no related function")

    async def serve(self):
        await websockets.serve(self.control, "127.0.0.1", 8765)

    async def __setOrderHandler(self, message):
        await OrderHandler(message).run()

    async def __setBillHandler(self, message):
        await BillHandler(message).run()

    async def __setDetailedListHandler(self, message):
        await DetailedListHandler(message).run()

    async def __setStatisticsHandler(self, message):
        await StatisticsHandler(message).run()

    async def __setSystemStatusHandler(self, message):
        await SystemStatusHandler(message).run()
