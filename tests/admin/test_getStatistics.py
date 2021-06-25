import pytest
import tests.Utils as Utils
import time

from datetime import datetime
from src.admin.StatisticsHandler import StatisticsHandler
from src.model import *


@pytest.mark.asyncio
async def test_getStatistics():
    """
    test_getStatistics 测试getStatistics函数
    """
    # 初始化数据库，该操作首先会清空数据库表，然后初始化几个Device
    Utils.initDB()

    await DBManager.create(
        Power,
        roomID="01-01-01",
        startTime=datetime(2021, 6, 19, 1, 0),
        endTime=datetime(2021, 6, 19, 2, 0),
        powerState=True,
    )

    await DBManager.create(
        TargetTem,
        roomID="01-01-01",
        startTime=datetime(2021, 6, 19, 1, 0),
        endTime=datetime(2021, 6, 19, 2, 0),
        targetTem=27,
    )

    await DBManager.create(
        WindSpeed,
        roomID="01-01-01",
        startTime=datetime(2021, 6, 19, 1, 0),
        endTime=datetime(2021, 6, 19, 2, 0),
        windSpeed=1,
    )

    await DBManager.create(
        ReachTem,
        roomID="01-01-01",
        timePoint=datetime(2021, 6, 19, 1, 30),
    )

    await DBManager.create(
        Scheduling, roomID="01-01-01", timePoint=datetime(2021, 6, 19, 1, 30)
    )

    await DBManager.create(
        Order,
        userID="Alice",
        roomID="01-01-01",
        orderID="1",
        createdTime=datetime(2021, 6, 19, 1, 0),
        finishedTime=datetime(2021, 6, 19, 2, 0),
        state="using",
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

    # 正确结果
    test = {
        "roomID": "01-01-01",
        "airConditionerUsedTimes": 1,
        "mostFrequentlyUsedTargetTemperature": 27,
        "mostFrequentlyUsedWindSpeed": "low",
        "targetTemperatureReachedTimes": 1,
        "scheduledTimes": 1,
        "numberOfdetailedListRecords": 1,
        "totalCost": 30,
    }
    testList = list()
    testList.append(test)
    test = {"statistics": testList}

    # 测试返回结果
    startTime = int(time.mktime(datetime(2021, 6, 19, 1, 0).timetuple()))
    endTime = int(time.mktime(datetime(2021, 6, 19, 2, 0).timetuple()))
    ans = await StatisticsHandler.getStatistics(startTime, endTime)

    # 判断是否相等
    assert test == ans
