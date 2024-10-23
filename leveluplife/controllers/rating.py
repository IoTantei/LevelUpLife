from typing import Sequence
from uuid import UUID

from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select
from loguru import logger
from leveluplife.models.error import (
    RatingAlreadyExistsError,
    RatingNotFoundError,
)
from leveluplife.models.rating import RatingCreate, RatingUpdate
from leveluplife.models.table import Rating


class RatingController:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_rating_by_task_and_user(
        self, task_id: UUID, user_id: UUID
    ) -> Rating | None:
        statement = select(Rating).where(
            Rating.task_id == task_id, Rating.user_id == user_id
        )
        result = self.session.exec(statement)
        return result.one_or_none()

    async def create_rating(self, rating_create: RatingCreate) -> Rating:
        logger.info(
            f"Creating rating for task: {rating_create.task_id} as user: {rating_create.user_id}"
        )
        existing_rating = self.get_rating_by_task_and_user(
            rating_create.task_id, rating_create.user_id
        )
        if existing_rating:
            raise RatingAlreadyExistsError(task_id=rating_create.task_id)

        new_rating = Rating(**rating_create.model_dump())
        self.session.add(new_rating)
        self.session.commit()
        self.session.refresh(new_rating)
        return new_rating

    async def get_ratings(self, offset: int, limit: int) -> Sequence[Rating]:
        logger.info("Getting ratings")
        return self.session.exec(select(Rating).offset(offset).limit(limit)).all()

    async def get_rating_by_id(self, rating_id: UUID) -> Rating:
        try:
            logger.info(f"Getting rating by id: {rating_id}")
            return self.session.exec(select(Rating).where(Rating.id == rating_id)).one()
        except NoResultFound:
            raise RatingNotFoundError(rating_id=rating_id)

    async def update_rating(
        self, rating_id: UUID, rating_update: RatingUpdate
    ) -> Rating:
        try:
            db_rating = self.session.exec(
                select(Rating).where(Rating.id == rating_id)
            ).one()
            db_rating_data = rating_update.model_dump(exclude_unset=True)
            db_rating.sqlmodel_update(db_rating_data)
            self.session.add(db_rating)
            self.session.commit()
            self.session.refresh(db_rating)
            logger.info(f"Updated rating: {db_rating.id}")
            return db_rating
        except NoResultFound:
            raise RatingNotFoundError(rating_id=rating_id)

    async def delete_rating(self, rating_id: UUID) -> None:
        try:
            db_rating = self.session.exec(
                select(Rating).where(Rating.id == rating_id)
            ).one()
            self.session.delete(db_rating)
            self.session.commit()
            logger.info(f"Deleted rating: {db_rating.id}")
        except NoResultFound:
            raise RatingNotFoundError(rating_id=rating_id)
