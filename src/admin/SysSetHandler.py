import asyncio


class SysSetHandler:
    async def run(self, websocket) -> None:
        await self.roomStateUpdate(websocket)

    async def roomStateUpdate(self, websocket) -> None:
        while True:
            pass
            await asyncio.sleep(1)
