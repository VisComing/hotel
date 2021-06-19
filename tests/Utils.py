import logging
import os

os.environ["DBNAME"] = "mock_hotel"
from src.model import *
import peewee


def createTables() -> None:
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


def initAllRooms() -> None:
    """
    initAllRooms 在tbDevice表中创建所有的RoomID
    """

    roomIDList = [
        "01-01-01",
        "01-01-02",
        "01-01-03",
        "01-02-01",
        "01-02-02",
        "01-02-03",
        "01-03-01",
        "01-03-02",
        "01-03-03",
    ]
    for roomID in roomIDList:
        try:
            Device.create(roomID=roomID)
        except peewee.IntegrityError:
            pass


def initDB():
    try:
        createTables()
    except Exception as e:
        logging.warn(e)
    WindSpeed.delete().execute()
    UsageRecord.delete().execute()
    TargetTem.delete().execute()
    Scheduling.delete().execute()
    ReachTem.delete().execute()
    Power.delete().execute()
    DetailListItem.delete().execute()
    Bill.delete().execute()
    Order.delete().execute()
    Device.delete().execute()
    initAllRooms()
