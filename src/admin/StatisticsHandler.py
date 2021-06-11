from jsonrpcserver import method, async_dispatch as dispatch


class StatisticsHandler:
    async def run(self, message, websocket) -> None:
        response = await dispatch(message)
        if response.wanted:
            await websocket.send(str(response))

    @method
    async def getStatistics(startTime: int, endTime: int) -> dict:
        return None
