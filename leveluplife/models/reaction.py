from enum import Enum
from uuid import UUID

from sqlmodel import Field

from leveluplife.models.shared import DBModel


class ReactionType(str, Enum):
    LIKE: str = "👍"
    DISLIKE: str = "👎"
    SAD: str = "😭"
    HAPPY: str = "😄"
    CRAZY: str = "🤪"
    LAUGHING: str = "😂"
    INLOVE: str = "🥰"
    DISAPPOINTING: str = "😞"

    @property
    def description(self) -> str:
        descriptions = {
            "👍": "The user likes the task",
            "👎": "The user dislikes the task",
            "😭": "The user is sad about the task",
            "😄": "The user is happy about the task",
            "🤪": "The user is crazy about the task",
            "😂": "The user is laughing about the task",
            "🥰": "The user is in love with the task",
            "😞": "The user is disappointed about the task",
        }
        return descriptions[self.value]


class ReactionBase(DBModel):
    user_id: UUID | None = Field(foreign_key="user.id")
    task_id: UUID | None = Field(foreign_key="task.id")
    reaction: ReactionType


class ReactionCreate(ReactionBase):
    pass


class ReactionUpdate(DBModel):
    reaction: ReactionType | None = None
