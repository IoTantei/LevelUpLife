from enum import Enum

from sqlmodel import Field

from leveluplife.models.shared import DBModel


class Type(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    LOVER = "lover"
    DAILY = "daily"

    @property
    def duration(self):
        durations = {"weekly": 7, "monthly": 30, "yearly": 365, "lover": 10, "daily": 1}
        return durations[self.value]


class QuestBase(DBModel):
    name: str = Field(max_length=144, unique=True, index=True)
    description: str = Field(max_length=369)
    xp_reward: int = Field(default=0)
    type: Type


class QuestCreate(QuestBase):
    pass


class QuestUpdate(DBModel):
    name: str | None = None
    description: str | None = None
    xp_reward: int | None = None
    type: Type | None = None
