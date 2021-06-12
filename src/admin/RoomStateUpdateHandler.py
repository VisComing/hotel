import asyncio
import logging
from src.model import *
from jsonrpcclient.clients.websockets_client import WebSocketsClient
import websockets


class RoomStateUpdateHandler:
    async def run(self, websocket) -> None:
        await self.roomStateUpdate(websocket)

    async def roomStateUpdate(self, websocket) -> None:
        # TODO @adslppp
        """
        roomStateUpdate 每隔一秒更新房间信息

        Args:
            websocket ([type]): 传入此连接
        """
        while True:
            # 选出所有的房间
            devices = await DBManager.execute(Device.select())
            infos = list()
            for device in devices:
                info = dict()
                info["roomID"] = device.roomID
                info["isStarted"] = device.isPower
                # 如果空调没开，就不传其余字段
                if device.isPower == True:
                    info["roomTemperature"] = device.currentTemperature
                    info["targetTemperature"] = device.targetTemperature
                    info["windSpeed"] = device.windSpeed
                    info["isSupplyingWind"] = device.isSupplyAir
                infos.append(info)
            try:
                await WebSocketsClient(websocket).notify(
                    method_name="roomStateUpdate", infos=infos
                )
            except websockets.exceptions.ConnectionClosedError as e:
                # 客户端断开连接异常
                logging.warning(e)
                # 退出while循环
                break
            await asyncio.sleep(1)
