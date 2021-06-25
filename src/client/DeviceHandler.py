"""
@TIME 2021/06/15
@Author Venessa Yang
@FileName DeviceHandler.py
@Description: The methods to handle the client events and the devices' info 
"""
import logging
from datetime import datetime
from operator import methodcaller

from peewee_async import select
from src.model.BaseModel import DBManager
from jsonrpcserver import method, async_dispatch as dispatch
from src.model.Device import Device
from src.model.Power import Power
from src.model.ReachTem import ReachTem
from src.model.TargetTem import TargetTem
from src.model.WindSpeed import WindSpeed

windDict = {"low": 1, "medium": 2, "high": 3}


class DeviceHandler:
    async def run(self, message: str, websocket) -> None:
        """
        run 使用jsonrpc将消息分派给不同函数

        Args:
            message (str): 收到的消息
        """
        response = await dispatch(message)
        if response.wanted:
            await websocket.send(str(response))

    @method
    async def PowerOn(roomID: str):
        """
        PowerOn 开机事件

        Args:
            roomID(str): 房间ID，格式 01-23-45

        Returns:
            比对当前温度和默认目标温度,如果不相等：
                修改device表中isAskAir项
            修改device表中的isPoweron
            向Power表中插入startTime、powerState
        """
        currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        tmpInfo = await DBManager.execute(
            Device.select().where(Device.roomID == roomID)
        )
        if tmpInfo[0].currentTemperature != tmpInfo[0].targetTemperature:
            await DBManager.execute(
                Device.update(isPower=True, isAskAir=True).where(
                    Device.roomID == roomID
                )
            )
        else:
            await DBManager.execute(
                Device.update(isPower=True).where(Device.roomID == roomID)
            )

        await DBManager.create(
            Power, roomID=roomID, startTime=currentTime, powerState=True
        )

        logging.info("Complete the {} poweron event...".format(roomID))
        return

    @method
    async def PowerOff(roomID: str):
        """
        PowerOff 关机事件

        Args:
            roomID(str): 房间ID，格式 01-23-45

        Returns:
            修改device表中的isPoweron、isAskAir
                找Power表中的最后一条，修改endTime、powerState
        """
        currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await DBManager.execute(
            Device.update(isPower=False, isAskAir=False).where(Device.roomID == roomID)
        )

        sTime = await DBManager.get(
            Power.select()
            .where(Power.roomID == roomID)
            .order_by(Power.startTime.desc())
        )
        await DBManager.execute(
            Power.update(endTime=currentTime).where(
                Power.roomID == roomID and Power.startTime == sTime.startTime
            )
        )
        await DBManager.create(
            Power,
            roomID=roomID,
            startTime=currentTime,
            powerState=False
        )

        logging.info("Complete the {} PowerOff event...".format(roomID))
        return

    @method
    async def AdjustTargetTemperature(roomID: str, targetTemperature: int):
        # TODO @Venessa Yang
        """
        AdjustTargetTemperature 调节目标温度事件

        Args:
            roomID(str): 房间ID，格式 01-23-45
            targetTemperature(int)：房间设置的目标温度

        Returns:
            修改Device中对应条目的目标温度信息
            创建TargetTem的一个条目
        """
        currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await DBManager.execute(
            Device.update(targetTemperature=targetTemperature).where(
                Device.roomID == roomID
            )
        )
        info = await DBManager.execute(
            TargetTem.select().where(TargetTem.roomID == roomID)
        )
        # 如果对于此房间来说 该用户不是第一次调整：即有记录，需要补充上一次的endTime
        if info:
            sTime = await DBManager.get(
                TargetTem.select()
                .where(TargetTem.roomID == roomID)
                .order_by(TargetTem.startTime.desc())
            )
            logging.info("The startTime is {}".format(sTime.startTime))
            await DBManager.execute(
                TargetTem.update(endTime=currentTime).where(
                    TargetTem.roomID == roomID
                    and TargetTem.startTime == sTime.startTime
                )
            )
        await DBManager.create(
            TargetTem, roomID=roomID, startTime=currentTime, targetTem=targetTemperature
        )

        logging.info("Complete the {} AdjustTargetTemperature info...".format(roomID))
        return

    @method
    async def AdjustWindSpeed(roomID: str, windSpeed: str):
        """
        AdjustWindSpeed 调节目标风速事件

        Args:
            roomID(str): 房间ID，格式 01-23-45
            windSpeed(str)：房间设置的风速

        Returns:
            修改Device中对应条目的风速信息
            创建WindSpeed表中对应条目
        """
        currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await DBManager.execute(
            Device.update(windSpeed=windDict[windSpeed]).where(Device.roomID == roomID)
        )
        # 如果对于此房间来说 该用户不是第一次调整：即有记录，需要补充上一次的endTime
        info = await DBManager.execute(
            WindSpeed.select().where(WindSpeed.roomID == roomID)
        )
        if info:
            sTime = await DBManager.get(
                WindSpeed.select()
                .where(WindSpeed.roomID == roomID)
                .order_by(WindSpeed.startTime.desc())
            )
            logging.info("The startTime is {}".format(sTime.startTime))
            await DBManager.execute(
                WindSpeed.update(endTime=currentTime).where(
                    WindSpeed.roomID == roomID
                    and WindSpeed.startTime == sTime.startTime
                )
            )
        await DBManager.create(
            WindSpeed,
            roomID=roomID,
            startTime=currentTime,
            windSpeed=windDict[windSpeed],
        )

        logging.info("Complete the {} AdjustWindSpeed event...".format(roomID))
        return

    @method
    async def ResumeWindSupply(roomID: str):
        """
        ResumeWindSupply 请求送风事件

        Args:
            roomID(str): 房间ID，格式 01-23-45

        Returns:
            修改Device中对应条目的isAskAir信息
        """
        await DBManager.execute(
            Device.update(isAskAir=True).where(Device.roomID == roomID)
        )
        logging.info("Complete the {} ResumeWindSupply event...".format(roomID))
        return

    @method
    async def SuspendWindSupply(roomID: str):
        """
        SuspendWindSupply 暂停送风事件[此刻房间温度达到目标温度]

        Args:
            roomID(str): 房间ID，格式 01-23-45

        Returns:
            创建reachTem的一个条目
            修改Device中对应条目的isAskAir信息
        """
        currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await DBManager.execute(
            Device.update(isAskAir=False).where(Device.roomID == roomID)
        )

        await DBManager.create(ReachTem, roomID=roomID, timePoint=currentTime)

        logging.info("Complete the {} SuspendWindSupply event...".format(roomID))
        return

    @method
    async def RoomTemperatureUpdate(roomID: str, roomTemperature: int):
        """
        RoomTemperatureUpdate 更新房间当前温度事件

        Args:
            roomID(str): 房间ID，格式 01-23-45
            currentTemperature(int)：当前温度

        Returns:
            修改Device中对应条目的currentTemperature信息
        """

        await DBManager.execute(
            Device.update(currentTemperature=roomTemperature).where(
                Device.roomID == roomID
            )
        )

        logging.info("Complete the {} RoomTemperatureUpdate event...".format(roomID))
        return

    @method
    async def GetConfiguration(roomID: str):
        """
        GetConfiguration 更新房间当前温度事件

        Args:
            roomID(str): 房间ID，格式 01-23-45

        Returns:
            系统默认配置信息
        """
        # 查settings表

        # 返回给客户端
        return {
            "temperatureControlMode": "heating",
            "targetTemperatureRange": {
                "heating": {"min": 18, "max": 26},
                "cooling": {"min": 26, "max": 30},
            },
            "defaultTemperature": 26,
        }
