import logging
from admin.AdminController import AdminController
import asyncio
from admin.BillHandler import BillHandler
from admin.DetailedListHandler import DetailedListHandler
from admin.DeviceHandler import DeviceHandler
from admin.OrderHandler import OrderHandler
from admin.StatisticsHandler import StatisticsHandler
from admin.SysConfigHandler import SysConfigHandler
from admin.SystemStatusHandler import SystemStatusHandler

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

    async def run(self):
        await self.adminController.serve()


if __name__ == "__main__":
    mainController = MainController()
    asyncio.get_event_loop().run_until_complete(mainController.run())
    asyncio.get_event_loop().run_forever()
