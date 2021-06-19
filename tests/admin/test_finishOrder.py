import pytest
import tests.Utils as Utils

from datetime import datetime
from src.admin.OrderHandler import OrderHandler
from src.model import *
from jsonrpcserver.exceptions import ApiError

@pytest.mark.asyncio
async def test_finishOrder():
    """
    test_finishOrder 测试createOrder函数
    """
    # 初始化数据库，该操作首先会清空数据库表，然后初始化几个Device
    Utils.initDB()

    time = datetime.now()
    await DBManager.create(
        Order,
        userID="Alice",
        roomID="01-01-01",
        orderID="1",
        createdTime=time,
        finishedTime=time,
        state="using",
    )
    await DBManager.create(
        Order,
        userID="Bob",
        roomID="01-01-02",
        orderID="2",
        createdTime=time,
        finishedTime=time,
        state="unpaid",
    )
    await DBManager.create(
        UsageRecord,
        orderID="1",
        startTime=time,
        endTime=time,
        windSpeed=3,
        cost=1,
        billingRate="1",
    )
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
    
    await OrderHandler.finishOrder(orderID="1")
    res = await DBManager.execute(Order.select().where(Order.orderID == "1"))
    orders = list(res)
    order = orders[0]

    # 测试正常情况
    # 测试订单状态已被修改
    assert order.state == "unpaid"
    # 测试完成时间被修改
    assert order.finishedTime != time
    # 测试使用记录被存入详单
    res = await DBManager.execute(
            DetailListItem.select().where(DetailListItem.orderID == "1")
    )
    assert len(res) == 1
    # 测试账单中添加了一条数据
    res = await DBManager.execute(Bill.select().where(Bill.orderID == "1"))
    assert len(res) == 1

    # 测试ApiError
    # 测试无效的订单ID
    with pytest.raises(ApiError, match="无效的订单ID") as excinfo:
        await OrderHandler.finishOrder("3")
    assert excinfo.type == ApiError
    # 测试非法的订单状态
    with pytest.raises(ApiError, match="非法的订单状态") as excinfo:
        await OrderHandler.finishOrder("2")
    assert excinfo.type == ApiError