import pytest
import tests.Utils as Utils

from src.model import *
from jsonrpcserver.exceptions import ApiError
from src.admin.SystemStatusHandler import SystemStatusHandler


@pytest.mark.asyncio
async def test_systemStatus():
    """
    test_systemStatus 测试getSystemStatus、startSystem、stopSystem函数
    """
    # 初始化数据库，该操作首先会清空数据库表，然后初始化几个Device
    Utils.initDB()
    # 首先获取系统状态，初始时为False
    status = await SystemStatusHandler.getSystemStatus()
    status = status["started"]
    assert status == False
    # 打开系统
    await SystemStatusHandler.startSystem()
    assert SystemStatusHandler.status == True
    # 测试 系统已经在运行中
    with pytest.raises(ApiError, match="系统已经在运行中") as excinfo:
        await SystemStatusHandler.startSystem()
    assert excinfo.type == ApiError
    # 关闭系统
    await SystemStatusHandler.stopSystem()
    assert SystemStatusHandler.status == False
    #测试 系统尚未启动
    with pytest.raises(ApiError, match="系统尚未启动") as excinfo:  
        await SystemStatusHandler.stopSystem()
    assert excinfo.type == ApiError
