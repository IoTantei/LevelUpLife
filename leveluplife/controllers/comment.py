from typing import Sequence
from uuid import UUID

from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select
from leveluplife.models.comment import CommentCreate, CommentUpdate
from leveluplife.models.error import CommentAlreadyExistsError, CommentNotFoundError
from leveluplife.models.table import Comment
from loguru import logger


class CommentController:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_comment_by_task_and_user(
        self, task_id: UUID, user_id: UUID
    ) -> Comment | None:
        statement = select(Comment).where(
            Comment.task_id == task_id, Comment.user_id == user_id
        )
        result = self.session.exec(statement)
        return result.one_or_none()

    async def create_comment(self, comment_create: CommentCreate) -> Comment:
        logger.info(
            f"Creating comment for task: {comment_create.task_id} as user: {comment_create.user_id}"
        )
        existing_comment = self.get_comment_by_task_and_user(
            comment_create.task_id, comment_create.user_id
        )
        if existing_comment:
            raise CommentAlreadyExistsError(task_id=comment_create.task_id)

        new_comment = Comment(**comment_create.model_dump())
        self.session.add(new_comment)
        self.session.commit()
        self.session.refresh(new_comment)
        return new_comment

    async def get_comments(self, offset: int, limit: int) -> Sequence[Comment]:
        logger.info("Getting comments")
        return self.session.exec(select(Comment).offset(offset).limit(limit)).all()

    async def get_comment_by_id(self, comment_id: UUID) -> Comment:
        try:
            logger.info(f"Getting comment by id: {comment_id}")
            return self.session.exec(
                select(Comment).where(Comment.id == comment_id)
            ).one()
        except NoResultFound:
            raise CommentNotFoundError(comment_id=comment_id)

    async def update_comment(
        self, comment_id: UUID, comment_update: CommentUpdate
    ) -> Comment:
        try:
            db_comment = self.session.exec(
                select(Comment).where(Comment.id == comment_id)
            ).one()
            db_comment_data = comment_update.model_dump(exclude_unset=True)
            db_comment.sqlmodel_update(db_comment_data)
            self.session.add(db_comment)
            self.session.commit()
            self.session.refresh(db_comment)
            logger.info(f"Updated comment: {db_comment.id}")
            return db_comment
        except NoResultFound:
            raise CommentNotFoundError(comment_id=comment_id)

    async def delete_comment(self, comment_id: UUID) -> None:
        try:
            db_comment = self.session.exec(
                select(Comment).where(Comment.id == comment_id)
            ).one()
            self.session.delete(db_comment)
            self.session.commit()
            logger.info(f"Deleted comment: {db_comment.id}")
        except NoResultFound:
            raise CommentNotFoundError(comment_id=comment_id)
