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

from src.client.ClientHandler import ClientHandler
from src.client.DeviceHandler import DeviceHandler
from src.client.ClientController import ClientController

from src.model import *
import peewee

# 配置logging
logging.basicConfig(
    filename="log.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)


class MainController:
    def __init__(self) -> None:
        """
        __init__ MainCOntroller构造函数，将各种handler注入到controller中
        """
        self.createTables()
        self.initAllRooms()
        self.initSettings()

        self.clientController = ClientController()
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

        self.clientController.setDeviceHandler(DeviceHandler())
        self.clientController.setClientHandler(ClientHandler())

    async def run(self) -> None:
        """
        run 运行adminController以及clientController
        """
        tasks = [self.adminController.serve(), self.clientController.serve()]
        await asyncio.wait(tasks)

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
        Settings.create_table(True)

    def initAllRooms(self) -> None:
        """
        initAllRooms 在tbDevice表中创建所有的RoomID
        """

        roomIDList = ["01-01-01", "01-01-02", "01-01-03", "01-01-04"]
        for roomID in roomIDList:
            try:
                Device.create(roomID=roomID)
            except peewee.IntegrityError:
                pass

    def initSettings(self) -> None:
        """
        initSettings 在第一次建立数据库时需要初始化系统设置
        """
        if len(Settings.select()) != 0:
            return
        Settings.create(
            temperatureControlMode="heating",
            minHeatTemperature=26,
            maxHeatTemperature=30,
            minCoolTemperature=18,
            maxCoolTemperature=26,
            defaultTemperature=26,
            electricityPrice=1,
            lowRate=1,
            midRate=2,
            highRate=3,
            maxNumOfClientsToServe=3,
        )


# 程序入口，启动事件循环
if __name__ == "__main__":
    mainController = MainController()
    asyncio.get_event_loop().run_until_complete(mainController.run())
    asyncio.get_event_loop().run_forever()
