import logging
import asyncio
from src.admin.BillHandler import BillHandler
from src.admin.DetailedListHandler import DetailedListHandler
from src.admin.OrderHandler import OrderHandler
from src.admin.StatisticsHandler import StatisticsHandler
from src.admin.SysConfigHandler import SysConfigHandler
from src.admin.RoomStateUpdateHandler import RoomStateUpdateHandler
from src.admin.SystemStatusHandler import SystemStatusHandler
from src.admin.PaymentHandler import PaymentHandler
from src.admin.AdminController import AdminController
from src.model import *
import peewee

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
        self.adminController.setRoomStateUpdateHandler(RoomStateUpdateHandler())
        self.adminController.setPaymentHandler(PaymentHandler())

        self.createTables()
        # self.initAllRooms()

    async def run(self) -> None:
        """
        run 运行adminController以及clientController
        """
        await self.adminController.serve()

    def createTables(self) -> None:
        """
        createTables 创建数据库表
        """
        Device.create_table(True)
        Order.create_table(True)
        Bill.create_table(True)
        DetailListItem.create_table(True)
        Power.create_table(True)
        ReachTem.create_table(True)
        Scheduling.create_table(True)
        TargetTem.create_table(True)
        UsageRecord.create_table(True)
        WindSpeed.create_table(True)

    def initAllRooms(self) -> None:
        """
        initAllRooms 在tbDevice表中创建所有的RoomID
        """

        def int2RoomID(num: int):
            id1 = str(num % 100).zfill(2)
            num = num // 100
            id2 = str(num % 100).zfill(2)
            num = num // 100
            id3 = str(num % 100).zfill(2)
            return id3 + "-" + id2 + "-" + id1

        for i in range(0, 999999):
            roomID = int2RoomID(i)
            try:
                Device.create(roomID=roomID)
            except peewee.IntegrityError:
                pass


# 程序入口，启动事件循环
if __name__ == "__main__":
    mainController = MainController()
    asyncio.get_event_loop().run_until_complete(mainController.run())
    asyncio.get_event_loop().run_forever()
