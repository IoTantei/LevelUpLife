from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID

from sqlmodel import Field

from leveluplife.models.quest import Type
from leveluplife.models.shared import DBModel


class UserItemLink(DBModel, table=True):
    user_id: UUID | None = Field(foreign_key="user.id", primary_key=True)
    item_id: UUID | None = Field(foreign_key="item.id", primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    equipped: bool = Field(default=False)


class UserItemLinkCreate(DBModel):
    user_ids: list[UUID]
    equipped: bool = Field(default=False)


class QuestStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"


class UserQuestLink(DBModel, table=True):
    user_id: UUID | None = Field(foreign_key="user.id", primary_key=True)
    quest_id: UUID | None = Field(foreign_key="quest.id", primary_key=True)
    quest_start: datetime = Field(default_factory=lambda: datetime.now())
    quest_end: datetime | None = Field(default=None)
    status: QuestStatus = Field(default=QuestStatus.ACTIVE)

    @classmethod
    def create(cls, quest_type: Type, **kwargs):
        instance = cls(**kwargs)
        instance.quest_end = instance.quest_start + timedelta(days=quest_type.duration)
        return instance

    def update_status(self):
        if self.quest_end and datetime.now() > self.quest_end:
            self.status = QuestStatus.EXPIRED


class UserQuestLinkCreate(DBModel):
    user_ids: list[UUID]
    quest_start: datetime | None = None
    quest_end: datetime | None = None
    status: QuestStatus = QuestStatus.ACTIVE
