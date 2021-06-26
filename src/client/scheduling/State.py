from __future__ import annotations
from typing import Literal, Union

from src.client.scheduling.Immutable import Immutable

WindSpeed = Literal[1, 2, 3]


class ServingState(Immutable):
    roomID: str
    state: Literal["serving"] = "serving"
    servingTime: float = 0
    windSpeed: WindSpeed


class WaitingState(Immutable):
    state: Literal["waiting"] = "waiting"
    roomID: str
    waitingTime: float = 0
    windSpeed: WindSpeed


class IdleState(Immutable):
    state: Literal["idle"] = "idle"
    roomID: str


class BillingInformationDelta(Immutable):
    billingRate: float
    servingTime: float
    cost: float


State = Union[ServingState, WaitingState, IdleState]


class ResumeAction(Immutable):
    name: Literal["resume"] = "resume"
    windSpeed: WindSpeed


class SuspendAction(Immutable):
    name: Literal["suspend"] = "suspend"


class AdjustWindSpeedAction(Immutable):
    name: Literal["adjust-wind-speed"] = "adjust-wind-speed"
    windSpeed: WindSpeed


Action = Union[ResumeAction, SuspendAction, AdjustWindSpeedAction]


def reducer(*, state: State, action: Action) -> State:
    if state.state == "serving":
        if action.name == "resume":
            return state
        elif action.name == "suspend":
            return IdleState(roomID=state.roomID)
        elif action.name == "adjust-wind-speed":
            return ServingState(
                roomID=state.roomID,
                servingTime=state.servingTime,
                windSpeed=action.windSpeed,
            )
        else:
            raise
    elif state.state == "waiting":
        if action.name == "resume":
            return state
        elif action.name == "suspend":
            return IdleState(roomID=state.roomID)
        elif action.name == "adjust-wind-speed":
            return WaitingState(
                roomID=state.roomID,
                waitingTime=state.waitingTime,
                windSpeed=action.windSpeed,
            )
        else:
            raise
    elif state.state == "idle":
        if action.name == "resume":
            return WaitingState(roomID=state.roomID, windSpeed=action.windSpeed)
        elif action.name == "suspend":
            return state
        elif action.name == "adjust-wind-speed":
            return state
        else:
            raise
    else:
        raise
