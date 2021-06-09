from jsonrpcserver import method, async_dispatch as dispatch


class SysConfigHandler:
    def __init__(self, message) -> None:
        self._message = message

    async def run(self):
        dispatch(self._message)

    @method
    def getSysConfig():
        pass

    @method
    def setSysConfig(newConfigration: dict):
        pass
