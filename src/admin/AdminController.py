import logging

from admin.SysConfigHandler import SysConfigHandler
from .OrderHandler import OrderHandler
from .BillHandler import BillHandler
from .DetailedListHandler import DetailedListHandler
from .StatisticsHandler import StatisticsHandler
from .SystemStatusHandler import SystemStatusHandler
import websockets
import json

# 如何发送消息？定时发送？
#


class AdminController:
    async def control(self, websocket, path):
        async for message in websocket:
            method = json.loads(message)["method"]
            if (
                method == "createOrder"
                or method == "fetchOrders"
                or method == "finishOrder"
            ):
                await self._orderHandle.run(message)
            elif method == "getBill":
                await self._billHandler.run(message)
            elif method == "getDetailedList":
                await self._detailedListHandler.run(message)
            elif method == "getStatistics":
                await self._statisticsHandler.run(message)
            elif (
                method == "getSystemStatus"
                or method == "startSystem"
                or method == "stopSystem"
            ):
                await self._systemStatusHandler.run(message)
            elif method == "getSysConfig" or method == "setSysConfig":
                await self._sysConfigHandler.run(message)
            else:
                logging.error("AdminController: rpc failed, no related function")

    def setOrderHandler(self, handler: OrderHandler):
        self._orderHandle = handler

    def setBillHandler(self, handler: BillHandler):
        self._billHandler = handler

    def setDetailedListHandler(self, handler: DetailedListHandler):
        self._detailedListHandler = handler

    def setStatisticsHandler(self, handler: StatisticsHandler):
        self._statisticsHandler = handler

    def setSystemStatusHandler(self, handler: SystemStatusHandler):
        self._systemStatusHandler = handler

    def setSysconfigHandler(self, handler: SysConfigHandler):
        self._sysConfigHandler = handler

    async def serve(self):
        await websockets.serve(self.control, "127.0.0.1", 8765)
