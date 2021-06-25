import logging
import time

from peewee import fn
from jsonrpcserver import method, async_dispatch as dispatch
from datetime import datetime

from peewee_async import select
from src.model import *


class StatisticsHandler:
    async def run(self, message, websocket) -> None:
        response = await dispatch(message)
        if response.wanted:
            await websocket.send(str(response))

    @method
    async def getStatistics(startTime: int, endTime: int) -> dict:
        # TODO @Jun丶
        """
        getStatistics [summary]

        Args:
            startTime (int): [description]
            endTime (int): [description]

        Returns:
            dict: [description]
        """
        logging.info("get statistics...")

        # 将unix时间戳转换为datetime格式
        startTime = datetime.fromtimestamp(startTime)
        endTime = datetime.fromtimestamp(endTime)

        # 选出所有在要求时段内有记录的房间：注意考虑部分时间在该时间段的情况
        # 只需保证空调运行的结束时间至少在要求时段开始之后且开始时间在要求时段结束之前
        rooms = await DBManager.execute(
            Power.select().where(Power.endTime > startTime & Power.startTime < endTime)
        )

        statistics = list()
        for room in rooms:
            # 计算空调使用次数
            useTimes = await DBManager.execute(
                Power.select().where(
                    (Power.powerState == 1)
                    & (Power.roomID == room.roomID)
                    & (Power.endTime > startTime)
                    & (Power.startTime < endTime)
                )
            )
            useTimes = len(useTimes)

            # 求出最常用目标温度
            # 先筛选出时间条件符合的常用目标温度记录,并计算每个温度的设定使用时长
            targetTem = await DBManager.execute(
                TargetTem.select(
                    TargetTem.targetTem,
                    fn.SUM(TargetTem.endTime - TargetTem.startTime).alias("totalTime"),
                )
                .where(
                    (TargetTem.endTime > startTime)
                    & (TargetTem.startTime < endTime)
                    & (TargetTem.roomID == room.roomID)
                )
                .group_by(TargetTem.targetTem)
            )
            totalTime = 0
            commonTem = 0
            for tem in targetTem:
                if tem.totalTime > totalTime:
                    totalTime = tem.totalTime
                    commonTem = tem.targetTem

            # 求出最常用风速,原理同最常用目标温度
            windSpeed = await DBManager.execute(
                WindSpeed.select(
                    WindSpeed.windSpeed,
                    fn.SUM(WindSpeed.endTime - WindSpeed.startTime).alias("totalTime"),
                )
                .where(
                    (WindSpeed.endTime > startTime)
                    & (WindSpeed.startTime < endTime)
                    & (WindSpeed.roomID == room.roomID)
                )
                .group_by(WindSpeed.windSpeed)
            )
            totalTime = 0
            commonWind = 0
            for wind in windSpeed:
                if tem.totalTime > totalTime:
                    totalTime = wind.totalTime
                    commonWind = wind.windSpeed
            if commonWind == 1:
                commonWindSpeed = "low"
            elif commonWind == 2:
                commonWindSpeed = "medium"
            elif commonWind == 3:
                commonWindSpeed = "high"

            # 计算达到目标温度次数
            reachTimes = await DBManager.execute(
                ReachTem.select().where(
                    (ReachTem.timePoint >= startTime)
                    & (ReachTem.timePoint <= endTime)
                    & (ReachTem.roomID == room.roomID)
                )
            )
            reachTimes = len(reachTimes)

            # 计算被调度次数
            scheduleTimes = await DBManager.execute(
                Scheduling.select().where(
                    (Scheduling.timePoint >= startTime)
                    & (Scheduling.timePoint <= endTime)
                    & (Scheduling.roomID == room.roomID)
                )
            )
            scheduleTimes = len(scheduleTimes)

            # 以roomID分类求解，orders表示一个roomID对应的所有订单
            # 计算详单记录数和总费用
            orders = await DBManager.execute(
                Order.select().where(Order.roomID == room.roomID)
            )
            detailTimes = 0
            totalCost = 0.0
            for order in orders:
                detaillists = await DBManager.execute(
                    DetailListItem.select().where(
                        (DetailListItem.orderID == order.orderID)
                        & (DetailListItem.endtime > startTime)
                        & (DetailListItem.startTime < endTime)
                    )
                )

                for item in detaillists:
                    detailTimes += 1
                    totalCost += item.cost

            statistic = {
                "roomID": room.roomID.roomID,
                "airConditionerUsedTimes": useTimes,
                "mostFrequentlyUsedTargetTemperature": commonTem,
                "mostFrequentlyUsedWindSpeed": commonWindSpeed,
                "targetTemperatureReachedTimes": reachTimes,
                "scheduledTimes": scheduleTimes,
                "numberOfdetailedListRecords": detailTimes,
                "totalCost": totalCost,
            }
            statistics.append(statistic)

        return {"statistics": statistics}
