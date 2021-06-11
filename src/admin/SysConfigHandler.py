from jsonrpcserver import method, async_dispatch as dispatch


class SysConfigHandler:
    async def run(self, message: str, websocket) -> None:
        response = await dispatch(message)
        if response.wanted:
            await websocket.send(str(response))

    @method
    def getSysConfig() -> dict:
        return {}

    @method
    def setSysConfig(newConfigration: dict) -> None:
        return None
