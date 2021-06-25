import pytest
import tests.Utils as Utils
import time

from datetime import datetime
from src.admin.DetailedListHandler import DetailedListHandler
from src.model import *


@pytest.mark.asyncio
async def test_getDetailedList():
    """
    test_getDetailedList 测试getDetailedList函数
    """
    # 初始化数据库，该操作首先会清空数据库表，然后初始化几个Device
    Utils.initDB()

    await DBManager.create(
        Order,
        userID="Alice",
        roomID="01-01-01",
        orderID="1",
        createdTime=datetime(2021, 6, 19, 1, 0),
        finishedTime=datetime(2021, 6, 19, 2, 0),
        state="unpaid",
    )
    await DBManager.create(
        DetailListItem,
        orderID="1",
        detailListID="11",
        startTime=datetime(2021, 6, 19, 1, 0),
        endtime=datetime(2021, 6, 19, 2, 0),
        windSpeed=1,
        cost=30,
        billingRate=0.5,
    )

    test = {
        "startTime": round(time.mktime(datetime(2021, 6, 19, 1, 0).timetuple())),
        "endTime": round(time.mktime(datetime(2021, 6, 19, 2, 0).timetuple())),
        "windSpeed": "low",
        "billingRate": 0.5,
    }
    testList = list()
    testList.append(test)
    test = {"items": testList}

    ans = await DetailedListHandler.getDetailedList("1")

    assert test == ans
