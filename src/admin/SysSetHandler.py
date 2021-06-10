import asyncio


class SysSetHandler:
    async def run(self, websocket):
        await self.roomStateUpdate(websocket)

    async def roomStateUpdate(self, websocket):
        while True:
            pass
            asyncio.sleep(1)
