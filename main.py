import logging

import asyncio

from src.admin.BillHandler import BillHandler
from src.admin.DetailedListHandler import DetailedListHandler
from src.admin.OrderHandler import OrderHandler
from src.admin.StatisticsHandler import StatisticsHandler
from src.admin.SysConfigHandler import SysConfigHandler
from src.admin.SysSetHandler import SysSetHandler
from src.admin.SystemStatusHandler import SystemStatusHandler
from src.admin.PaymentHandler import PaymentHandler
from src.admin.AdminController import AdminController

# 配置logging
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


class MainController:
    def __init__(self) -> None:
        """
        __init__ MainCOntroller构造函数，将各种handler注入到controller中
        """
        self.adminController = AdminController()
        # 依赖注入
        self.adminController.setOrderHandler(OrderHandler())
        self.adminController.setBillHandler(BillHandler())
        self.adminController.setDetailedListHandler(DetailedListHandler())
        self.adminController.setStatisticsHandler(StatisticsHandler())
        self.adminController.setSystemStatusHandler(SystemStatusHandler())
        self.adminController.setSysconfigHandler(SysConfigHandler())
        self.adminController.setSysSetHandler(SysSetHandler())
        self.adminController.setPaymentHandler(PaymentHandler())

    async def run(self) -> None:
        """
        run 运行adminController以及clientController
        """
        await self.adminController.serve()


# 程序入口，启动事件循环
if __name__ == "__main__":
    mainController = MainController()
    asyncio.get_event_loop().run_until_complete(mainController.run())
    asyncio.get_event_loop().run_forever()
