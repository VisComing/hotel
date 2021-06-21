import pytest
import tests.Utils as Utils
import time

from datetime import datetime
from src.admin.SysConfigHandler import SysConfigHandler
from src.model import *


@pytest.mark.asyncio
async def test_getSysConfig():
    """
    test_getSysConfig 测试getSysConfig函数
    """
    # 初始化数据库，该操作首先会清空数据库表，然后初始化几个Device
    Utils.initDB()

    await DBManager.create(
        Settings,
        temperatureControlMode="heating",
        minHeatTemperature=18,
        maxHeatTemperature=26,
        minCoolTemperature=26,
        maxCoolTemperature=30,
        defaultTemperature=26,
        electricityPrice=1,
        lowRate=1,
        midRate=2,
        highRate=3,
        maxNumOfClientsToServe=3,
    )

    ans = {
        "temperatureControlMode": "heating",
        "targetTemperatureRange": {
            "heating": {"min": 18, "max": 26},
            "cooling": {"min": 26, "max": 30},
        },
        "defaultTemperature": 26,
        "electricityPrice": 1,
        "electricityConsumptionRate": {"low": 1, "medium": 2, "high": 3},
        "maxNumOfClientsToServe": 3,
    }

    res = await SysConfigHandler.getSysConfig()

    assert res == ans
