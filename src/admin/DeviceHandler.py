import asyncio
from jsonrpcclient.clients.websockets_client import WebSocketsClient
from jsonrpcserver import method, async_dispatch as dispatch

class DeviceHandler:
    async def setDeviceHandler(self, ws, message):
        await dispatch(message)
        pass
    
    @method
    async def createOrder():
        pass
    @method
    async def fetchOrders():
        pass
    @method
    async def finishOrder():
        pass
    @method
    async def getBill():
        pass
    @method
    async def getDetailedList():
        pass
    @method
    async def getStatistics():
        pass
    @method
    async def getSystemStatus():
        pass
    @method
    async def startSystem():
        pass
    @method
    async def stopSystem():
        pass
    @method
    async def getSysConfig():
        pass
    @method
    async def setSysConfig():
        pass

deviceHandler = DeviceHandler()