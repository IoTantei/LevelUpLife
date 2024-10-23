from typing import Sequence
from uuid import UUID

from sqlalchemy.exc import NoResultFound
from sqlmodel import select

from leveluplife.models.error import ReactionAlreadyExistsError, ReactionNotFoundError
from leveluplife.models.reaction import ReactionCreate, ReactionUpdate
from leveluplife.models.table import Reaction
from loguru import logger


class ReactionController:
    def __init__(self, session) -> None:
        self.session = session

    def get_reaction_by_task_and_user(self, task_id, user_id) -> Reaction | None:
        statement = select(Reaction).where(
            Reaction.task_id == task_id, Reaction.user_id == user_id
        )
        result = self.session.exec(statement)
        return result.one_or_none()

    async def create_reaction(self, reaction_create: ReactionCreate) -> Reaction:
        logger.info(
            f"Creating reaction for task: {reaction_create.task_id} as user: {reaction_create.user_id}"
        )
        existing_reaction = self.get_reaction_by_task_and_user(
            reaction_create.task_id, reaction_create.user_id
        )
        if existing_reaction:
            raise ReactionAlreadyExistsError(task_id=reaction_create.task_id)

        new_reaction = Reaction(**reaction_create.model_dump())
        self.session.add(new_reaction)
        self.session.commit()
        self.session.refresh(new_reaction)
        return new_reaction

    async def get_reactions(self, offset: int, limit: int) -> Sequence[Reaction]:
        logger.info("Getting reactions")
        return self.session.exec(select(Reaction).offset(offset).limit(limit)).all()

    async def get_reaction_by_id(self, reaction_id: UUID) -> Reaction:
        try:
            logger.info(f"Getting reaction by id: {reaction_id}")
            return self.session.exec(
                select(Reaction).where(Reaction.id == reaction_id)
            ).one()
        except NoResultFound:
            raise ReactionNotFoundError(reaction_id=reaction_id)

    async def update_reaction(
        self, reaction_id: UUID, reaction_update: ReactionUpdate
    ) -> Reaction:
        try:
            db_reaction = self.session.exec(
                select(Reaction).where(Reaction.id == reaction_id)
            ).one()
            db_reaction_data = reaction_update.model_dump(exclude_unset=True)
            db_reaction.sqlmodel_update(db_reaction_data)
            self.session.add(db_reaction)
            self.session.commit()
            self.session.refresh(db_reaction)
            logger.info(f"Updated comment: {db_reaction.id}")
            return db_reaction
        except NoResultFound:
            raise ReactionNotFoundError(reaction_id=reaction_id)

    async def delete_reaction(self, reaction_id: UUID) -> None:
        try:
            db_reaction = self.session.exec(
                select(Reaction).where(Reaction.id == reaction_id)
            ).one()
            self.session.delete(db_reaction)
            self.session.commit()
            logger.info(f"Deleted reaction: {db_reaction.id}")
        except NoResultFound:
            raise ReactionNotFoundError(reaction_id=reaction_id)
