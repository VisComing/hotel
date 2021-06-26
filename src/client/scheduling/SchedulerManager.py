from __future__ import annotations
from typing import Iterable, Mapping, Sequence
import itertools

from src.client.scheduling.Scheduler import SchedulerInterface, Scheduler
from src.client.scheduling.State import *


class SchedulerManager:
    lastStates: Mapping[str, State]
    actions: Mapping[str, Sequence[Action]]

    scheduler: SchedulerInterface

    def __init__(self, *, scheduler: SchedulerInterface, rooms: Iterable[str]) -> None:
        self.scheduler = scheduler

        self.lastStates = dict(
            map(lambda roomID: (roomID, IdleState(roomID=roomID)), rooms)
        )
        self.actions = {}

    @staticmethod
    def addAction(
        *, actions: Mapping[str, Sequence[Action]], roomID: str, action: Action
    ) -> Mapping[str, Sequence[Action]]:
        newActions = dict(actions)
        newActions.setdefault(roomID, ())
        newActions[roomID] = tuple(
            itertools.chain.from_iterable([newActions[roomID], (action,)])
        )

        return newActions

    @staticmethod
    def applyActions(
        *, states: Mapping[str, State], actions: Mapping[str, Sequence[Action]]
    ) -> Mapping[str, State]:
        states = dict(states)

        for key, state in states.items():
            newState = state

            for action in actions.get(key, ()):
                newState = reducer(state=newState, action=action)

            states[key] = newState

        return states

    @staticmethod
    def increaseStateTimer(
        *, states: Mapping[str, State], lastStates: Mapping[str, State]
    ) -> Mapping[str, State]:
        states = dict(states)

        for key, state in states.items():
            oldState = lastStates[key]

            if state.state == "serving" and oldState.state == "serving":
                states[key] = ServingState(
                    roomID=state.roomID,
                    windSpeed=state.windSpeed,
                    servingTime=state.servingTime + 1,
                )
            elif state.state == "waiting" and oldState.state == "waiting":
                states[key] = WaitingState(
                    roomID=state.roomID,
                    windSpeed=state.windSpeed,
                    waitingTime=state.waitingTime + 1,
                )

        return states

    def dispatchAction(self, *, roomID: str, action: Action):
        self.actions = SchedulerManager.addAction(
            actions=self.actions, roomID=roomID, action=action
        )

    def tick(self):
        lastStates = self.lastStates

        statesAfterActions = SchedulerManager.applyActions(
            states=lastStates, actions=self.actions
        )
        self.actions = {}

        statesReadyForScheuling = SchedulerManager.increaseStateTimer(
            states=statesAfterActions, lastStates=lastStates
        )

        statesAfterScheuling = self.scheduler.schedule(states=statesReadyForScheuling)

        self.lastStates = statesAfterScheuling

        return (lastStates, statesReadyForScheuling, statesAfterScheuling)
