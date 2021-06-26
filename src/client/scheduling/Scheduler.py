from __future__ import annotations
from typing import Dict, List, Mapping, Sequence, Tuple

from src.client.scheduling.State import *
from src.settings import devConfig

from abc import abstractmethod, ABC


class SchedulerInterface(ABC):
    @abstractmethod
    def schedule(self, *, states: Mapping[str, State]) -> Mapping[str, State]:
        raise NotImplementedError()


class Scheduler(SchedulerInterface):
    maxNumOfClientsToServe: int

    def __init__(self, *, maxNumOfClientsToServe: int = 3):
        self.maxNumOfClientsToServe = maxNumOfClientsToServe

    def replace(
        self, *, servings: Sequence[ServingState], waitings: Sequence[WaitingState]
    ) -> Tuple[Sequence[ServingState], Sequence[WaitingState]]:
        servingQueue = sorted(servings, key=lambda it: (it.windSpeed, -it.servingTime))
        waitingQueue = sorted(waitings, key=lambda it: (-it.windSpeed, it.waitingTime))

        toWaitings: List[ServingState] = []
        toServings: List[WaitingState] = []

        for _ in range(0, self.maxNumOfClientsToServe - len(servingQueue)):
            if waitingQueue:
                toServings.append(waitingQueue.pop(0))
            else:
                break

        for _ in range(0, len(waitingQueue)):
            new = waitingQueue.pop(0)
            if servingQueue:
                top = servingQueue.pop(0)

                if top.windSpeed < new.windSpeed:
                    toServings.append(new)
                    toWaitings.append(top)
                elif (
                    top.windSpeed == new.windSpeed
                    and top.servingTime
                    >= devConfig.minServingTime / devConfig.timeScaleFactor
                ):
                    toServings.append(new)
                    toWaitings.append(top)
                else:
                    break
            else:
                break

        return (toWaitings, toServings)

    def schedule(self, *, states: Mapping[str, State]) -> Mapping[str, State]:
        servings: List[ServingState] = []
        waitings: List[WaitingState] = []
        for it in states.values():
            if it.state == "serving":
                servings.append(it)
            elif it.state == "waiting":
                waitings.append(it)

        toWaitings, toServings = self.replace(servings=servings, waitings=waitings)

        newStates: Dict[str, State] = dict(states)
        for state in toWaitings:
            newStates[state.roomID] = WaitingState(
                roomID=state.roomID, windSpeed=state.windSpeed
            )
        for state in toServings:
            newStates[state.roomID] = ServingState(
                roomID=state.roomID, windSpeed=state.windSpeed
            )

        return newStates
