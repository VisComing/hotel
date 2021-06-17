import pytest
import tests.Utils as Utils


from src.admin.OrderHandler import OrderHandler
from src.model import *


@pytest.mark.asyncio
async def test_createOrder():
    """
    test_create_order 测试createOrder函数
    """
    # 初始化数据库，该操作首先会清空数据库表，然后初始化几个Device
    Utils.initDB()
    # 执行该函数，注意OrderHandler不用加括号
    res = await OrderHandler.createOrder(userID="zrf", roomID="01-01-01")
    # createOrder应该会成功，返回之中包含orderID
    assert "orderID" in res
    # 同时，可以从数据库中查出该orderID
    res = await DBManager.execute(
        Order().select().where(Order.orderID == res["orderID"])
    )
    assert len(res) == 1
