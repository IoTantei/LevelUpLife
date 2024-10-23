from datetime import datetime
from typing import Sequence
from uuid import UUID

from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import Session, select
from loguru import logger

from leveluplife.models.error import (
    QuestAlreadyExistsError,
    QuestNotFoundError,
    QuestInUserNotFoundError,
    QuestAlreadyInUserError,
)
from leveluplife.models.quest import QuestCreate, QuestUpdate
from leveluplife.models.relationship import (
    UserQuestLinkCreate,
    UserQuestLink,
    QuestStatus,
)
from leveluplife.models.table import Quest, User
from leveluplife.models.view import QuestWithUser


class QuestController:
    def __init__(self, session: Session) -> None:
        self.session = session

    async def create_quest(self, quest_create: QuestCreate) -> Quest:
        try:
            new_quest = Quest(**quest_create.model_dump())
            self.session.add(new_quest)
            self.session.commit()
            self.session.refresh(new_quest)
            logger.info(f"New quest created: {new_quest.name}")
            return new_quest
        except IntegrityError:
            raise QuestAlreadyExistsError(_name=quest_create.name)

    async def update_quest(self, quest_id: UUID, quest_update: QuestUpdate) -> Quest:
        try:
            db_quest = self.session.exec(
                select(Quest).where(Quest.id == quest_id)
            ).one()
            db_item_data = quest_update.model_dump(exclude_unset=True)
            db_quest.sqlmodel_update(db_item_data)
            self.session.add(db_quest)
            db_quest.updated_at = datetime.now()
            self.session.commit()
            self.session.refresh(db_quest)
            logger.info(f"Updated quest: {db_quest.name}")
            return db_quest
        except NoResultFound:
            raise QuestNotFoundError(quest_id=quest_id)

    async def delete_quest(self, quest_id: UUID) -> None:
        try:
            db_quest = self.session.exec(
                select(Quest).where(Quest.id == quest_id)
            ).one()
            self.session.delete(db_quest)
            db_quest.updated_at = datetime.now()
            self.session.commit()
            logger.info(f"Deleted quest: {db_quest.name}")
        except NoResultFound:
            raise QuestNotFoundError(quest_id=quest_id)

    async def get_quests(self, offset: int, limit: int) -> Sequence[Quest]:
        logger.info("Getting quests")
        return self.session.exec(select(Quest).offset(offset).limit(limit)).all()

    async def get_quest_by_id(self, quest_id: UUID) -> Quest:
        try:
            logger.info(f"Getting quest by id: {quest_id}")
            return self.session.exec(select(Quest).where(Quest.id == quest_id)).one()
        except NoResultFound:
            raise QuestNotFoundError(quest_id=quest_id)

    async def assign_quest_to_user(
        self,
        quest_id: UUID,
        user_quest_link_create: UserQuestLinkCreate,
        quest_start: datetime,
        quest_end: datetime | None = None,
        status: QuestStatus = QuestStatus.ACTIVE,
    ) -> QuestWithUser:
        try:
            quest = self.session.exec(select(Quest).where(Quest.id == quest_id)).one()
            users = []
            for user_id in user_quest_link_create.user_ids:
                user = self.session.exec(select(User).where(User.id == user_id)).one()
                users.append(user)

                user_quest_link = UserQuestLink(
                    user_id=user_id,
                    quest_id=quest_id,
                    quest_start=quest_start,
                    quest_end=quest_end,
                    status=status,
                )
                self.session.add(user_quest_link)

            self.session.commit()
            self.session.refresh(quest)

            return QuestWithUser(**quest.model_dump(), users=users)
        except NoResultFound:
            raise QuestNotFoundError(quest_id=quest_id)
        except IntegrityError:
            self.session.rollback()
            raise QuestAlreadyInUserError(username=user.username, quest_id=quest_id)

    async def remove_quest_from_user(self, quest_id: UUID, user_id: UUID) -> None:
        try:
            user_quest_link = self.session.exec(
                select(UserQuestLink)
                .where(UserQuestLink.quest_id == quest_id)
                .where(UserQuestLink.user_id == user_id)
            ).one()
            self.session.delete(user_quest_link)
            self.session.commit()
        except NoResultFound:
            raise QuestInUserNotFoundError(quest_id=quest_id, user_id=user_id)
