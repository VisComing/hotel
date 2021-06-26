import logging
import websockets
import json
import asyncio

from src.settings import websocketsConfig
from src.client.DeviceHandler import DeviceHandler
from src.client.ClientHandler import ClientHandler


class ClientController:
    async def control(self, websocket, path):
        """
        control 处理该连接的消息

        Args:
            websocket (websockets): 连接对象
            path: 不可省略该参数
        """
        try:
            roomID = ""
            async for message in websocket:
                logging.info(message)
                method = json.loads(message)["method"]
                if (
                    method == "PowerOn"
                    or method == "PowerOff"
                    or method == "AdjustTargetTemperature"
                    or method == "AdjustWindSpeed"
                    or method == "ResumeWindSupply"
                    or method == "SuspendWindSupply"
                    or method == "RoomTemperatureUpdate"
                    or method == "GetConfiguration"
                ):
                    params = json.loads(message)["params"]
                    roomID = params["roomID"]
                    self._ClientHandler.addConnection(roomID, websocket)
                    await self._DeviceHandler.run(message, websocket)
                else:
                    logging.error("ClientController: rpc failed, no related function")
            self._ClientHandler.removeConnectionByID(roomID)
        except websockets.exceptions.ConnectionClosed as e:
            logging.warning(e)
            self._ClientHandler.removeConnectionBySocket(roomID)

    def setDeviceHandler(self, handler: DeviceHandler) -> None:
        """
        setDeviceHandler 接受外部注入的DeviceHandler

        Args:
            handler (DeviceHandler): 外部注入DeviceHandler

        Returns:
            None: 返回空
        """
        self._DeviceHandler = handler

    def setClientHandler(self, handler: ClientHandler) -> None:
        """
        setClientHandler 接受外部注入的ClientHandler

        Args:
            handler (ClientHandler): 外部注入ClientHandler

        Returns:
            None: 返回空
        """
        self._ClientHandler = handler

    async def serve(self):
        """
        serve 监听端口，处理连接
        """
        # await websockets.serve(
        #    self.control, websocketsConfig.CLIENTHOST, websocketsConfig.CLIENTPORT
        # )

        tasks = [
            self._ClientHandler.run(),
            websockets.serve(
                self.control, websocketsConfig.CLIENTHOST, websocketsConfig.CLIENTPORT
            ),
        ]
        await asyncio.wait(tasks)
