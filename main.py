import logging

import asyncio

from src.admin.BillHandler import BillHandler
from src.admin.DetailedListHandler import DetailedListHandler
from src.admin.OrderHandler import OrderHandler
from src.admin.StatisticsHandler import StatisticsHandler
from src.admin.SysConfigHandler import SysConfigHandler
from src.admin.SysSetHandler import SysSetHandler
from src.admin.SystemStatusHandler import SystemStatusHandler
from src.admin.AdminController import AdminController
from src.model.Order import Order
from src.model.BaseModel import DBManager


logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


class MainController:
    def __init__(self) -> None:
        self.adminController = AdminController()
        # 依赖注入
        self.adminController.setOrderHandler(OrderHandler())
        self.adminController.setBillHandler(BillHandler())
        self.adminController.setDetailedListHandler(DetailedListHandler())
        self.adminController.setStatisticsHandler(StatisticsHandler())
        self.adminController.setSystemStatusHandler(SystemStatusHandler())
        self.adminController.setSysconfigHandler(SysConfigHandler())
        self.adminController.setSysSetHandler(SysSetHandler())

    async def run(self) -> None:
        # await DBManager.create(Order, userID='zhou', orderID='1s23')
        await self.adminController.serve()


if __name__ == "__main__":
    mainController = MainController()
    asyncio.get_event_loop().run_until_complete(mainController.run())
    asyncio.get_event_loop().run_forever()
