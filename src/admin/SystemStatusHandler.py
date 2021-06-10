from jsonrpcserver import method, async_dispatch as dispatch


class SystemStatusHandler:
    async def run(self):
        await dispatch(self._message)

    @method
    async def getSystemStatus():
        pass

    @method
    async def startSystem():
        pass

    @method
    async def stopSystem():
        pass
