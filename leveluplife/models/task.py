from uuid import UUID

from sqlmodel import Field

from leveluplife.models.shared import DBModel


class TaskBase(DBModel):
    title: str = Field(default=None, max_length=80, index=True, unique=True)
    description: str = Field(max_length=400)
    completed: bool
    category: str
    user_id: UUID | None = Field(foreign_key="user.id")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(DBModel):
    description: str | None = None
    completed: bool | None = None
    category: str | None = None
    title: str | None = None
