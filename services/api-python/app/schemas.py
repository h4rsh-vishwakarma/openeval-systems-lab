from typing import Any, Literal
from pydantic import BaseModel, Field

from .models import State


class TaskCreate(BaseModel):
    scenario: Literal["webhook_once"] = "webhook_once"
    input: dict[str, Any] = Field(default_factory=dict)


class Submission(BaseModel):
    implementation: Literal["golden", "defective_duplicate", "defective_validation"]
    inject_failure: Literal["none", "timeout", "invalid_output", "transient"] = "none"


class TaskView(BaseModel):
    id: str
    tenant_id: str
    state: State
    attempts: int
    spec: dict[str, Any]
    result: dict[str, Any] | None
    error: str | None

    model_config = {"from_attributes": True}


class ErrorBody(BaseModel):
    error: dict[str, str]
