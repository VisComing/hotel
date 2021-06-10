from jsonrpcserver import method, async_dispatch as dispatch


class StatisticsHandler:
    async def run(self):
        await dispatch(self._message)

    @method
    async def getStatistics(startTime: int, endTime: int):
        pass
