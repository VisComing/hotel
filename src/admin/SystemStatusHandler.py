from jsonrpcserver import method, async_dispatch as dispatch


class SystemStatusHandler:
    async def run(self) -> None:
        await dispatch(self._message)

    @method
    async def getSystemStatus() -> dict:
        return {}

    @method
    async def startSystem() -> dict:
        return {}

    @method
    async def stopSystem() -> dict:
        return {}
