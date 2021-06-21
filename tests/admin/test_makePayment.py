import pytest
import tests.Utils as Utils
import time

from datetime import datetime
from src.admin.PaymentHandler import PaymentHandler
from src.model import *
from jsonrpcserver.exceptions import ApiError

@pytest.mark.asyncio
async def test_makePayment():
    """
    test_makePayment 测试makePayment函数
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
    await PaymentHandler.makePayment("1")
    ans = await DBManager.execute(Order.select().where(Order.orderID == "1"))
    ans = list(ans)
    state = ans[0].state
    # 测试正常情况
    assert state == "completed"

    # 测试无效的订单ID
    with pytest.raises(ApiError, match = "无效的订单ID") as excinfo:
        await PaymentHandler.makePayment("3")
    assert excinfo.type == ApiError

    # 测试非法的订单状态：unpaid是合法状态
    with pytest.raises(ApiError, match = "非法的订单状态") as excinfo:
        await PaymentHandler.makePayment("2")
    assert excinfo.type == ApiError
