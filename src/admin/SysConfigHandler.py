from jsonrpcserver import method, async_dispatch as dispatch


class SysConfigHandler:
    async def run(self) -> None:
        dispatch(self._message)

    @method
    def getSysConfig() -> dict:
        return {}

    @method
    def setSysConfig(newConfigration: dict) -> dict:
        return {}
