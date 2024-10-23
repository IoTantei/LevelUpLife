from uuid import UUID
from sqlmodel import Field
from leveluplife.models.shared import DBModel


class RatingBase(DBModel):
    rating: int = Field(default=0, ge=0, le=10)
    user_id: UUID | None = Field(foreign_key="user.id")
    task_id: UUID | None = Field(foreign_key="task.id")


class RatingCreate(RatingBase):
    pass


class RatingUpdate(DBModel):
    rating: int | None = None
