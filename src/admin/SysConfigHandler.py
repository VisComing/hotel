from jsonrpcserver import method, async_dispatch as dispatch


class SysConfigHandler:
    async def run(self):
        dispatch(self._message)

    @method
    def getSysConfig():
        pass

    @method
    def setSysConfig(newConfigration: dict):
        pass
