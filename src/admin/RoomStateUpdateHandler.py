import asyncio


class RoomStateUpdateHandler:
    async def run(self, websocket) -> None:
        await self.roomStateUpdate(websocket)

    async def roomStateUpdate(self, websocket) -> None:
        while True:
            pass
            await asyncio.sleep(1)
