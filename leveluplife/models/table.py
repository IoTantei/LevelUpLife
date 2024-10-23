from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from leveluplife.models.comment import CommentBase
from leveluplife.models.item import ItemBase
from leveluplife.models.quest import QuestBase
from leveluplife.models.rating import RatingBase
from leveluplife.models.reaction import ReactionBase
from leveluplife.models.relationship import UserItemLink, UserQuestLink
from leveluplife.models.task import TaskBase
from leveluplife.models.user import UserBase


class User(UserBase, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True, unique=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    strength: int = 0
    intelligence: int = 0
    agility: int = 0
    wise: int = 0
    psycho: int = 0
    experience: int = 0
    password: str = Field(min_length=4)
    tasks: list["Task"] = Relationship(back_populates="user")
    items: list["Item"] = Relationship(back_populates="users", link_model=UserItemLink)
    ratings: list["Rating"] = Relationship(back_populates="user")
    comments: list["Comment"] = Relationship(back_populates="user")
    reactions: list["Reaction"] = Relationship(back_populates="user")
    quests: list["Quest"] = Relationship(
        back_populates="users", link_model=UserQuestLink
    )


class Task(TaskBase, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True, unique=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    user: User | None = Relationship(back_populates="tasks")
    ratings: list["Rating"] = Relationship(back_populates="task")
    comments: list["Comment"] = Relationship(back_populates="task")
    reactions: list["Reaction"] = Relationship(back_populates="task")


class Item(ItemBase, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True, unique=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime | None = Field(default=None)
    deleted_at: datetime | None = Field(default=None)
    users: list["User"] = Relationship(back_populates="items", link_model=UserItemLink)


class Rating(RatingBase, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True, unique=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    user: User | None = Relationship(back_populates="ratings")
    task: Task | None = Relationship(back_populates="ratings")


class Comment(CommentBase, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True, unique=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime | None = Field(default=None)
    deleted_at: datetime | None = Field(default=None)
    user: User | None = Relationship(back_populates="comments")
    task: Task | None = Relationship(back_populates="comments")


class Reaction(ReactionBase, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True, unique=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime | None = Field(default=None)
    deleted_at: datetime | None = Field(default=None)
    user: User | None = Relationship(back_populates="reactions")
    task: Task | None = Relationship(back_populates="reactions")


class Quest(QuestBase, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True, unique=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime | None = Field(default=None)
    deleted_at: datetime | None = Field(default=None)
    users: list["User"] = Relationship(
        back_populates="quests", link_model=UserQuestLink
    )
