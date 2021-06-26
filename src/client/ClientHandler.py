import asyncio
import itertools

from peewee import fn
from src.client.scheduling.State import (
    AdjustWindSpeedAction,
    ResumeAction,
    SuspendAction,
    State,
)
from src.client.scheduling.Scheduler import Scheduler
from src.client.scheduling.SchedulerManager import SchedulerManager
from typing import Dict, Iterable, List, Literal, Mapping
from src.model import *
from datetime import datetime
import math
from jsonrpcclient.clients.websockets_client import WebSocketsClient
import websockets
import logging

from websockets import WebSocketCommonProtocol


class ClientHandler:
    sockets: Mapping[str, WebSocketCommonProtocol]
    manager: SchedulerManager

    def __init__(self):
        self.sockets = {}

        rooms = map(lambda it: it.roomID, Device.select())
        self.manager = SchedulerManager(scheduler=Scheduler(), rooms=rooms)

    def addConnection(self, roomID: str, socket: WebSocketCommonProtocol):
        if roomID in self.sockets:
            self.removeConnectionByID(roomID)

        self.sockets = dict(
            itertools.chain.from_iterable([self.sockets.items(), ((roomID, socket),)])
        )

    def removeConnectionByID(self, roomID: str):
        self.sockets = dict(filter(lambda t: t[0] != roomID, self.sockets.items()))

    def removeConnectionBySocket(self, socket: WebSocketCommonProtocol):
        self.sockets = dict(filter(lambda t: t[1] != socket, self.sockets.items()))

    async def notify(self, roomID: str, **kargs):
        if roomID not in self.sockets:
            return
        try:
            await WebSocketsClient(self.sockets[roomID]).notify(**kargs)
        except websockets.exceptions.ConnectionClosed:
            self.removeConnectionByID(roomID)

    async def dispatchActionsByDeviceStates(self) -> None:
        devices = list(await DBManager.execute(Device.select()))

        for device in devices:
            roomID = device.roomID

            if device.isPower and device.isAskAir:
                self.manager.dispatchAction(
                    roomID=roomID, action=ResumeAction(windSpeed=device.windSpeed)
                )
            else:
                self.manager.dispatchAction(roomID=roomID, action=SuspendAction())

            if device.windSpeed:
                self.manager.dispatchAction(
                    roomID=roomID, action=AdjustWindSpeedAction(windSpeed=device.windSpeed)
                )

    async def updateAndSendWindSupplyState(
        self, lastStates: Mapping[str, State], newStates: Mapping[str, State]
    ) -> None:
        windSpeedNumberToString: Dict[Literal[0, 1, 2], str] = {
            1: "low",
            2: "medium",
            3: "high",
        }

        for roomID, oldState in lastStates.items():
            newState = newStates[roomID]

            if oldState != newState:
                if newState.state == "serving":
                    await self.notify(
                        roomID,
                        method_name="WindSupplyResumed",
                        windSpeed=windSpeedNumberToString[newState.windSpeed],
                    )
                elif newState.state == "waiting":
                    await self.notify(
                        roomID, method_name="WindSupplySuspended", reason="scheduling"
                    )
                elif newState.state == "idle":
                    await self.notify(
                        roomID,
                        method_name="WindSupplySuspended",
                        reason="client-requested",
                    )
                else:
                    raise

                await DBManager.execute(
                    Device.update(isSupplyAir=(newState.state == "serving")).where(
                        Device.roomID == roomID
                    )
                )

    async def updateAndSendBillingInformation(self, lastStates: Mapping[str, State]):
        for roomID, state in lastStates.items():
            billingRate = 0
            if state.state == "serving":
                billingRate = state.windSpeed * 1 / 60

            device = await DBManager.get(Device.select().where(Device.roomID == roomID))
            totalCost = device.cost + billingRate * 1
            totalServiceTime = device.supplyTime + (
                1 if state.state == "serving" else 0
            )

            await self.notify(
                roomID,
                method_name="BillingInformationUpdate",
                billingRate=billingRate,
                totalCost=totalCost,
                totalServiceTime=totalServiceTime,
            )

            await DBManager.execute(
                Device.update(cost=totalCost, supplyTime=totalServiceTime).where(
                    Device.roomID == roomID
                )
            )

    async def updateUsageRecord(self, lastStates: Mapping[str, State]):
        now = datetime.now()

        for roomID, state in lastStates.items():
            billingRate = 0
            if state.state == "serving":
                billingRate = state.windSpeed * 1 / 60

            orders = list(
                await DBManager.execute(
                    Order.select().where(
                        (Order.roomID == roomID) & (Order.state == "using")
                    )
                )
            )

            if not orders:
                continue

            orderID = orders[0].orderID

            records = list(
                await DBManager.execute(
                    UsageRecord.select()
                    .where(
                        (UsageRecord.orderID == orderID)
                        & (UsageRecord.startTime == UsageRecord.endTime)
                    )
                    .order_by(UsageRecord.startTime)
                    .limit(1)
                )
            )

            if not records:
                if not billingRate:
                    continue

                await DBManager.execute(
                    UsageRecord.insert(
                        orderID=orderID,
                        startTime=now,
                        endTime=now,
                        windSpeed=state.windSpeed,
                        cost=0,
                        billingRate=billingRate,
                    )
                )
            else:
                record = records[0]

                if not math.isclose(record.billingRate, billingRate, rel_tol=10e-4):
                    await DBManager.execute(
                        UsageRecord.update(
                            endTime=now,
                            cost=(now - record.startTime).total_seconds()
                            * record.billingRate,
                        ).where(
                            (UsageRecord.orderID == orderID)
                            & (UsageRecord.startTime == record.startTime)
                        )
                    )

                    if not billingRate:
                        continue

                    await DBManager.execute(
                        UsageRecord.insert(
                            orderID=orderID,
                            startTime=now,
                            endTime=now,
                            windSpeed=state.windSpeed,
                            cost=0,
                            billingRate=billingRate,
                        )
                    )

    async def run(self) -> None:
        while True:
            baseTime = datetime.now()

            await self.dispatchActionsByDeviceStates()
            (lastStates, newStates) = self.manager.tick()

            await self.updateAndSendBillingInformation(lastStates)
            await self.updateAndSendWindSupplyState(lastStates, newStates)
            await self.updateUsageRecord(lastStates)

            delta = (datetime.now() - baseTime).total_seconds()
            await asyncio.sleep(1 - delta)
