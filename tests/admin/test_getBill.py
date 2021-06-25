import pytest
import tests.Utils as Utils
import time

from datetime import datetime
from src.admin.BillHandler import BillHandler
from src.model import *
from jsonrpcserver.exceptions import ApiError
from src.settings import adminErrorCode


@pytest.mark.asyncio
async def test_getBill():
    """
    test_getBill 测试getBill函数
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
        Order,
        userID="Bob",
        roomID="01-01-02",
        orderID="2",
        createdTime=datetime(2021, 6, 19, 1, 0),
        finishedTime=datetime(2021, 6, 19, 2, 0),
        state="using",
    )
    await DBManager.create(
        Bill,
        orderID="1",
        billID="11",
        totalCost=10,
    )
    await DBManager.create(
        Bill,
        orderID="2",
        billID="21",
        totalCost=10,
    )

    # 正确结果
    test = {
        "orderID": "1",
        "billID": "11",
        "totalCost": 10,
    }
    # 测试正常情况
    ans = await BillHandler.getBill("1")
    assert test == ans

    # 测试无效的订单ID
    with pytest.raises(ApiError, match="无效的订单ID") as excinfo:
        await BillHandler.getBill("3")
    assert excinfo.type == ApiError

    # 测试非法的订单状态
    with pytest.raises(ApiError, match="非法的订单状态") as excinfo:
        await BillHandler.getBill("2")
    assert excinfo.type == ApiError
