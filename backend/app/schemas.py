from typing import Literal

from pydantic import BaseModel, Field

Level = Literal["easy", "standard", "hard"]


class SessionCreate(BaseModel):
    locale: Literal["en", "ru"] = "en"
    scenario: str = "webshop"
    speed: Literal["test", "fast", "demo"] = "demo"
    already_planned: bool = True
    risk: bool = False
    raci: bool = False
    difficulty_cost: Level = "standard"
    difficulty_schedule: Level = "standard"
    difficulty_quality: Level = "standard"
    difficulty_motivation: Level = "standard"
    difficulty_risk: Level = "standard"


class Action(BaseModel):
    client_action_id: str | None = Field(default=None, max_length=64)


class AssignmentIn(BaseModel):
    activity_no: int
    resource_no: int
    percent: int = Field(ge=0, le=100)


class AssignmentsIn(Action):
    assignments: list[AssignmentIn]


class DecisionIn(Action):
    option: str = Field(max_length=16)  # option key or "postpone"
