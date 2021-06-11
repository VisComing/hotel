from jsonrpcserver import method, async_dispatch as dispatch


class SystemStatusHandler:
    async def run(self, message: str, websocket) -> None:
        response = await dispatch(message)
        if response.wanted:
            await websocket.send(str(response))

    @method
    async def getSystemStatus() -> dict:
        return {}

    @method
    async def startSystem() -> None:
        return None

    @method
    async def stopSystem() -> None:
        return None
