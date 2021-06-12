from jsonrpcserver import method, async_dispatch as dispatch


class SysConfigHandler:
    async def run(self, message: str, websocket) -> None:
        response = await dispatch(message)
        if response.wanted:
            await websocket.send(str(response))

    @method
    def getSysConfig() -> dict:
        # TODO @Jun丶
        """
        getSysConfig [summary]

        Returns:
            dict: [description]
        """
        return {}

    @method
    def setSysConfig(newConfigration: dict) -> None:
        # TODO @Jun丶
        """
        setSysConfig [summary]

        Args:
            newConfigration (dict): [description]

        Returns:
            [type]: [description]
        """
        return None
