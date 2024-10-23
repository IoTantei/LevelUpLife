from typing import Sequence
from uuid import UUID
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import Session, select
from leveluplife.models.error import (
    TaskAlreadyExistsError,
    TaskNotFoundError,
    TaskTitleNotFoundError,
)
from leveluplife.models.table import Task
from leveluplife.models.task import TaskCreate, TaskUpdate


class TaskController:
    def __init__(self, session: Session) -> None:
        self.session = session

    async def create_task(self, task_create: TaskCreate) -> Task:
        try:
            new_task = Task(**task_create.model_dump())
            self.session.add(new_task)
            self.session.commit()
            self.session.refresh(new_task)
            logger.info(f"New task created: {new_task.title}")
            return new_task
        except IntegrityError:
            raise TaskAlreadyExistsError(title=task_create.title)

    async def get_tasks(self, offset: int, limit: int) -> Sequence[Task]:
        logger.info("Getting tasks")
        return self.session.exec(select(Task).offset(offset).limit(limit)).all()

    async def get_task_by_id(self, task_id: UUID) -> Task:
        try:
            logger.info(f"Getting task by id: {task_id}")
            return self.session.exec(select(Task).where(Task.id == task_id)).one()
        except NoResultFound:
            raise TaskNotFoundError(task_id=task_id)

    async def get_task_by_title(self, task_title: str) -> Task:
        try:
            logger.info(f"Getting task by title: {task_title}")
            return self.session.exec(select(Task).where(Task.title == task_title)).one()
        except NoResultFound:
            raise TaskTitleNotFoundError(task_title=task_title)

    async def update_task(self, task_id: UUID, task_update: TaskUpdate) -> Task:
        try:
            db_task = self.session.exec(select(Task).where(Task.id == task_id)).one()
            db_task_data = task_update.model_dump(exclude_unset=True)
            db_task.sqlmodel_update(db_task_data)
            self.session.add(db_task)
            self.session.commit()
            self.session.refresh(db_task)
            logger.info(f"Updated task: {db_task.title}")
            return db_task
        except NoResultFound:
            raise TaskNotFoundError(task_id=task_id)

    async def delete_task(self, task_id: UUID) -> None:
        try:
            db_task = self.session.exec(select(Task).where(Task.id == task_id)).one()
            self.session.delete(db_task)
            self.session.commit()
            logger.info(f"Deleted task: {db_task.title}")
        except NoResultFound:
            raise TaskNotFoundError(task_id=task_id)
