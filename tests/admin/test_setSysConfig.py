import pytest
import tests.Utils as Utils

from src.admin.SysConfigHandler import SysConfigHandler
from src.model import *
from jsonrpcserver.exceptions import ApiError
from src.admin.SystemStatusHandler import SystemStatusHandler


@pytest.mark.asyncio
async def test_setSysConfig():
    """
    test_setSysConfig 测试setSysConfig函数
    """
    # 初始化数据库，该操作首先会清空数据库表，然后初始化几个Device
    Utils.initDB()

    newConfigration = {
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

    await SysConfigHandler.setSysConfig(newConfigration)
    settings = await DBManager.execute(Settings.select())

    settings = list(settings)
    settings = settings[0]

    res = {
        "temperatureControlMode": settings.temperatureControlMode,
        "targetTemperatureRange": {
            "heating": {
                "min": settings.minHeatTemperature,
                "max": settings.maxHeatTemperature,
            },
            "cooling": {
                "min": settings.minCoolTemperature,
                "max": settings.maxCoolTemperature,
            },
        },
        "defaultTemperature": settings.defaultTemperature,
        "electricityPrice": settings.electricityPrice,
        "electricityConsumptionRate": {
            "low": settings.lowRate,
            "medium": settings.midRate,
            "high": settings.highRate,
        },
        "maxNumOfClientsToServe": settings.maxNumOfClientsToServe,
    }

    assert newConfigration == res

    # 测试“禁止在运行时设置系统配置”
    SystemStatusHandler.status = True
    with pytest.raises(ApiError, match="禁止在运行时设置系统配置") as excinfo:
        await SysConfigHandler.setSysConfig(newConfigration)
    assert excinfo.type == ApiError
