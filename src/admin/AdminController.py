import logging
from src.admin.BillHandler import BillHandler
from src.admin.DetailedListHandler import DetailedListHandler
from src.admin.OrderHandler import OrderHandler
from src.admin.StatisticsHandler import StatisticsHandler
from src.admin.SysConfigHandler import SysConfigHandler
from src.admin.SystemStatusHandler import SystemStatusHandler
from src.admin.RoomStateUpdateHandler import RoomStateUpdateHandler
from src.admin.PaymentHandler import PaymentHandler
import websockets
import json
import asyncio
from src.settings import websocketsConfig


class AdminController:
    async def control(self, websocket, path):
        """
        control 处理该连接的消息

        Args:
            websocket (websockets): 连接对象
            path: 不可省略该参数
        """

        async def recvMessage():
            """
            recvMessage 接受消息，根据消息内容分派给不同的handler
            """
            try:
                async for message in websocket:
                    method = json.loads(message)["method"]
                    if (
                        method == "createOrder"
                        or method == "fetchOrders"
                        or method == "finishOrder"
                    ):
                        await self._orderHandle.run(message, websocket)
                    elif method == "getBill":
                        await self._billHandler.run(message, websocket)
                    elif method == "getDetailedList":
                        await self._detailedListHandler.run(message, websocket)
                    elif method == "getStatistics":
                        await self._statisticsHandler.run(message, websocket)
                    elif (
                        method == "getSystemStatus"
                        or method == "startSystem"
                        or method == "stopSystem"
                    ):
                        await self._systemStatusHandler.run(message, websocket)
                    elif method == "getSysConfig" or method == "setSysConfig":
                        await self._sysConfigHandler.run(message, websocket)
                    else:
                        logging.error(
                            "AdminController: rpc failed, no related function"
                        )
            except websockets.exceptions.ConnectionClosedError as e:
                logging.warning(e)

        # 并行执行接受消息函数，设置定时发送消息的handler
        tasks = [recvMessage(), self._roomStateUpdateHandler.run(websocket)]
        await asyncio.wait(tasks)

    def setOrderHandler(self, handler: OrderHandler) -> None:
        """
        setOrderHandler 接受外部注入的OrderHandler

        Args:
            handler (OrderHandler): 外部注入OrderHandler

        Returns:
            None: 返回空
        """
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

    def setRoomStateUpdateHandler(self, handler: RoomStateUpdateHandler):
        self._roomStateUpdateHandler = handler

    def setPaymentHandler(self, handler: PaymentHandler):
        self._sysPaymentHandler = handler

    async def serve(self):
        """
        serve 监听端口，处理连接
        """
        await websockets.serve(
            self.control, websocketsConfig.ADMINHOST, websocketsConfig.ADMINPORT
        )
