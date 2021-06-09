import logging
from admin.AdminController import AdminController
import asyncio

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


class MainController:
    def __init__(self) -> None:
        self.adminController = AdminController()

    async def run(self):
        await self.adminController.serve()


if __name__ == "__main__":

    mainController = MainController()
    asyncio.get_event_loop().run_until_complete(mainController.run())
    asyncio.get_event_loop().run_forever()
