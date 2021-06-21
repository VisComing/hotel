import logging
from jsonrpcserver import method, async_dispatch as dispatch
from src.model import *
from jsonrpcserver.exceptions import ApiError
from src.settings import adminErrorCode

class SystemStatusHandler:
    async def run(self, message: str, websocket) -> None:
        response = await dispatch(message)
        if response.wanted:
            await websocket.send(str(response))

    status = False

    @method
    async def getSystemStatus() -> dict:
        # TODO @Jun丶
        """
        getSystemStatus [summary]

        Returns:
            dict: [description]
        """
        logging.info("get system status...")
        return {"started": SystemStatusHandler.status}

    @method
    async def startSystem() -> None:
        # TODO @Jun丶
        """
        startSystem 启动系统

        """
        logging.info("start system...")
        if SystemStatusHandler.status == True:
            raise ApiError("系统已经在运行中", code=adminErrorCode.START_SYSTEM_SYSTEM_IS_RUNNING)
        
        SystemStatusHandler.status = True

        return None

    @method
    async def stopSystem() -> None:
        # TODO @Jun丶
        """
        stopSystem 停止系统

        """
        logging.info("stop system...")
        if SystemStatusHandler.status == False:
            raise ApiError("系统尚未启动", code=adminErrorCode.START_SYSTEM_SYSTEM_IS_RUNNING)
        
        SystemStatusHandler.status = False


        return None
