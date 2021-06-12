from jsonrpcserver import method, async_dispatch as dispatch


class SystemStatusHandler:
    async def run(self, message: str, websocket) -> None:
        response = await dispatch(message)
        if response.wanted:
            await websocket.send(str(response))

    @method
    async def getSystemStatus() -> dict:
        # TODO @Jun丶
        """
        getSystemStatus [summary]

        Returns:
            dict: [description]
        """
        return {}

    @method
    async def startSystem() -> None:
        # TODO @Jun丶
        """
        startSystem [summary]

        Returns:
            [type]: [description]
        """
        return None

    @method
    async def stopSystem() -> None:
        # TODO @Jun丶
        """
        stopSystem [summary]

        Returns:
            [type]: [description]
        """
        return None
