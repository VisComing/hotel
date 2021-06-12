import asyncio


class RoomStateUpdateHandler:
    async def run(self, websocket) -> None:
        await self.roomStateUpdate(websocket)

    async def roomStateUpdate(self, websocket) -> None:
        # TODO @adslppp
        """
        roomStateUpdate [summary]

        Args:
            websocket ([type]): [description]
        """
        while True:
            pass
            await asyncio.sleep(1)
