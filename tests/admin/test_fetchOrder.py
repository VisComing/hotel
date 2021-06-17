import pytest
import tests.Utils as Utils
import time

from datetime import datetime
from src.admin.OrderHandler import OrderHandler
from src.model import *


@pytest.mark.asyncio
async def test_fetchOrder():
    """
    test_create_order 测试createOrder函数
    """
    # 初始化数据库，该操作首先会清空数据库表，然后初始化几个Device
    Utils.initDB()

    crtime = datetime.now()
    fitime = datetime.now()
    await DBManager.create(
        Order,
        userID="Alice",
        roomID="01-01-01",
        orderID="1",
        createdTime=crtime,
        finishedTime=fitime,
        state="using",
    )
    await DBManager.create(
        Order,
        userID="Bob",
        roomID="01-02-01",
        orderID="2",
        createdTime=crtime,
        finishedTime=fitime,
        state="using",
    )

    # 测试完整条件获取订单
    filter = {"userID": "Alice", "roomID": "01-01-01", "state": "using"}
    res = await OrderHandler.fetchOrders(filter)
    ans = {
        "orders": [
            {
                "orderID": "1",
                "userID": "Alice",
                "roomID": "01-01-01",
                "createdTime": int(time.mktime(crtime.timetuple())),
                "finishedTime": int(time.mktime(fitime.timetuple())),
                "state": "using",
            }
        ]
    }
    assert res == ans

    # 测试无条件获取订单
    filter = {}
    res = await OrderHandler.fetchOrders(filter)
    ans = {
        "orders": [
            {
                "orderID": "1",
                "userID": "Alice",
                "roomID": "01-01-01",
                "createdTime": int(time.mktime(crtime.timetuple())),
                "finishedTime": int(time.mktime(fitime.timetuple())),
                "state": "using",
            },
            {
                "orderID": "2",
                "userID": "Bob",
                "roomID": "01-02-01",
                "createdTime": int(time.mktime(crtime.timetuple())),
                "finishedTime": int(time.mktime(fitime.timetuple())),
                "state": "using",
            }
        ]
    }
    assert res == ans


