from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    """Valid Kanban task statuses."""

    BACKLOG = "BACKLOG"
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    DONE = "DONE"

class TaskPriority(str, Enum):
    """Valid task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskBase(BaseModel):
    """Shared fields used when creating or updating a task."""

    title: str = Field(
        ...,
        min_length = 1,
        max_length = 100,
    )

    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM

class TaskCreate(TaskBase):
    """Request schema for creating a task."""

    pass

class TaskUpdate(BaseModel):
    """Request schema for updating a task."""

    title: str | None = Field(
        default = None,
        min_length = 1,
        max_length = 100,
    )
    description: str | None = None
    priority: TaskPriority | None = None

class TaskStatusUpdate(BaseModel):
    """Request schema for changing a task's Kanban status."""

    status: TaskStatus

class TaskResponse(TaskBase):
    """Response schema returned by the API."""

    id: int
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}