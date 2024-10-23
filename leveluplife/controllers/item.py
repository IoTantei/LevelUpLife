from datetime import datetime
from typing import Sequence
from uuid import UUID
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import Session, select
from leveluplife.models.error import (
    ItemAlreadyExistsError,
    ItemNameNotFoundError,
    ItemNotFoundError,
    ItemAlreadyInUserError,
    ItemInUserNotFoundError,
)
from leveluplife.models.item import ItemCreate, ItemUpdate
from leveluplife.models.relationship import UserItemLink, UserItemLinkCreate
from leveluplife.models.table import Item, User
from leveluplife.models.view import ItemWithUser


class ItemController:
    def __init__(self, session: Session) -> None:
        self.session = session

    async def create_item(self, item_create: ItemCreate) -> Item:
        try:
            new_item = Item(**item_create.model_dump())
            self.session.add(new_item)
            self.session.commit()
            self.session.refresh(new_item)
            logger.info(f"New item created: {new_item.name}")
            return new_item
        except IntegrityError:
            raise ItemAlreadyExistsError(_name=item_create.name)

    async def update_item(self, item_id: UUID, item_update: ItemUpdate) -> Item:
        try:
            db_item = self.session.exec(select(Item).where(Item.id == item_id)).one()
            db_item_data = item_update.model_dump(exclude_unset=True)
            db_item.sqlmodel_update(db_item_data)
            self.session.add(db_item)
            db_item.updated_at = datetime.now()
            self.session.commit()
            self.session.refresh(db_item)
            logger.info(f"Updated item: {db_item.name}")
            return db_item
        except NoResultFound:
            raise ItemNotFoundError(item_id=item_id)

    async def delete_item(self, item_id: UUID) -> None:
        try:
            db_item = self.session.exec(select(Item).where(Item.id == item_id)).one()
            self.session.delete(db_item)
            db_item.updated_at = datetime.now()
            self.session.commit()
            logger.info(f"Deleted item: {db_item.name}")
        except NoResultFound:
            raise ItemNotFoundError(item_id=item_id)

    async def get_items(self, offset: int, limit: int) -> Sequence[Item]:
        logger.info("Getting items")
        return self.session.exec(select(Item).offset(offset).limit(limit)).all()

    async def get_item_by_id(self, item_id: UUID) -> Item:
        try:
            logger.info(f"Getting item by id: {item_id}")
            return self.session.exec(select(Item).where(Item.id == item_id)).one()
        except NoResultFound:
            raise ItemNotFoundError(item_id=item_id)

    async def get_item_by_name(self, item_name: str) -> Item:
        try:
            logger.info(f"Getting item by name: {item_name}")
            return self.session.exec(select(Item).where(Item.name == item_name)).one()
        except NoResultFound:
            raise ItemNameNotFoundError(item_name=item_name)

    async def give_item_to_user(
        self,
        item_id: UUID,
        user_item_link_create: UserItemLinkCreate,
        equipped: bool = False,
    ) -> ItemWithUser:
        try:
            item = self.session.exec(select(Item).where(Item.id == item_id)).one()
            users = []
            for user_id in user_item_link_create.user_ids:
                user = self.session.exec(select(User).where(User.id == user_id)).one()
                users.append(user)

                user_item_link = UserItemLink(
                    user_id=user_id, item_id=item_id, equipped=equipped
                )
                self.session.add(user_item_link)

                if equipped:
                    item.equipped = equipped

            self.session.commit()
            self.session.refresh(item)

            return ItemWithUser(**item.model_dump(), users=users)
        except NoResultFound:
            raise ItemNotFoundError(item_id=item_id)
        except IntegrityError:
            self.session.rollback()
            raise ItemAlreadyInUserError(username=user.username, item_id=item_id)

    async def remove_item_from_user(self, item_id: UUID, user_id: UUID) -> None:
        try:
            user_item_link = self.session.exec(
                select(UserItemLink)
                .where(UserItemLink.item_id == item_id)
                .where(UserItemLink.user_id == user_id)
            ).one()
            self.session.delete(user_item_link)
            self.session.commit()
        except NoResultFound:
            raise ItemInUserNotFoundError(item_id=item_id, user_id=user_id)
