from uuid import UUID

from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import Session, select

from leveluplife.auth.hash import get_password_hash
from leveluplife.models.error import (
    UserEmailAlreadyExistsError,
    UserEmailNotFoundError,
    UserNotFoundError,
    UserUsernameAlreadyExistsError,
    UserUsernameNotFoundError,
    ItemLinkToUserNotFoundError,
)
from leveluplife.models.relationship import UserItemLink, UserQuestLink
from leveluplife.models.table import User, Item, Task, Rating, Comment, Reaction, Quest
from leveluplife.models.user import Tribe, UserCreate, UserUpdate
from leveluplife.models.view import (
    TaskView,
    UserView,
    ItemUserView,
    RatingView,
    CommentView,
    ReactionView,
    QuestUserView,
)


class UserController:
    def __init__(self, session: Session) -> None:
        self.session = session

    async def create_user(self, user_create: UserCreate) -> User:
        try:
            hashing_password = get_password_hash(user_create.password)

            # Calculate initial stats based on the tribe
            initial_stats = self.calculate_initial_stats(user_create.tribe)

            # Create new user
            new_user = User(**user_create.model_dump(), **initial_stats)
            new_user.password = hashing_password
            self.session.add(new_user)
            self.session.commit()
            self.session.refresh(new_user)
            logger.info(f"New user created: {new_user.username}")
            return new_user

        except IntegrityError:
            self.session.rollback()
            existing_user_by_email = self.session.exec(
                select(User).where(User.email == user_create.email)
            ).first()
            if existing_user_by_email:
                raise UserEmailAlreadyExistsError(email=user_create.email)
            existing_user_by_username = self.session.exec(
                select(User).where(User.username == user_create.username)
            ).first()
            if existing_user_by_username:
                raise UserUsernameAlreadyExistsError(username=user_create.username)

    @staticmethod
    def calculate_initial_stats(tribe: Tribe) -> dict[str, int]:
        if tribe == Tribe.NOSFERATI:
            return {
                "intelligence": 8,
                "strength": 2,
                "agility": 2,
                "wise": 1,
                "psycho": 10,
            }
        elif tribe == Tribe.VALHARS:
            return {
                "intelligence": 1,
                "strength": 10,
                "agility": 6,
                "wise": 6,
                "psycho": 2,
            }
        elif tribe == Tribe.SAHARANS:
            return {
                "intelligence": 9,
                "strength": 2,
                "agility": 3,
                "wise": 10,
                "psycho": 1,
            }
        elif tribe == Tribe.GLIMMERKINS:
            return {
                "intelligence": 10,
                "strength": 2,
                "agility": 2,
                "wise": 7,
                "psycho": 4,
            }
        else:
            return {
                "intelligence": 5,
                "strength": 5,
                "agility": 5,
                "wise": 5,
                "psycho": 5,
            }

    async def get_users(self, offset: int, limit: int) -> list[UserView]:
        logger.info("Getting users")
        user_with_items = self.session.exec(
            select(
                User,
                UserItemLink,
                Item,
                Task,
                Rating,
                Comment,
                Reaction,
                UserQuestLink,
                Quest,
            )
            .join(UserItemLink, User.id == UserItemLink.user_id, isouter=True)
            .join(Item, UserItemLink.item_id == Item.id, isouter=True)
            .join(Task, User.id == Task.user_id, isouter=True)
            .join(Rating, User.id == Rating.user_id, isouter=True)
            .join(Comment, User.id == Comment.user_id, isouter=True)
            .join(Reaction, User.id == Reaction.user_id, isouter=True)
            .join(UserQuestLink, User.id == UserQuestLink.user_id, isouter=True)
            .join(Quest, UserQuestLink.quest_id == Quest.id, isouter=True)
            .order_by(User.username)
            .offset(offset)
            .limit(limit)
        ).all()
        return self._construct_user_views(user_with_items)

    async def get_user_by_username(self, user_username: str) -> UserView:
        logger.info(f"Getting user by username: {user_username}")
        user_with_items = self.session.exec(
            select(User, UserItemLink, Item, UserQuestLink, Quest)
            .join(UserItemLink, User.id == UserItemLink.user_id, isouter=True)
            .join(Item, UserItemLink.item_id == Item.id, isouter=True)
            .join(UserQuestLink, User.id == UserQuestLink.user_id, isouter=True)
            .join(Quest, UserQuestLink.quest_id == Quest.id, isouter=True)
            .where(User.username == user_username)
        ).all()
        if not user_with_items:
            raise UserUsernameNotFoundError(user_username=user_username)
        return self._construct_user_view(user_with_items)

    async def get_user_by_username_with_password(self, user_username: str) -> User:
        return self.session.exec(
            select(User).where(User.username == user_username)
        ).one()

    async def get_user_by_email(self, user_email: str) -> UserView:
        logger.info(f"Getting user by email: {user_email}")
        user_with_items = self.session.exec(
            select(User, UserItemLink, Item, UserQuestLink, Quest)
            .join(UserItemLink, User.id == UserItemLink.user_id, isouter=True)
            .join(Item, UserItemLink.item_id == Item.id, isouter=True)
            .join(UserQuestLink, User.id == UserQuestLink.user_id, isouter=True)
            .join(Quest, UserQuestLink.quest_id == Quest.id, isouter=True)
            .where(User.email == user_email)
        ).all()
        if not user_with_items:
            raise UserEmailNotFoundError(user_email=user_email)
        return self._construct_user_view(user_with_items)

    async def get_users_by_tribe(
        self, user_tribe: Tribe, offset: int, limit: int
    ) -> list[UserView]:
        logger.info(f"Getting users by tribe: {user_tribe}")
        user_with_items = self.session.exec(
            select(
                User,
                UserItemLink,
                Item,
                Task,
                Rating,
                Comment,
                Reaction,
                UserQuestLink,
                Quest,
            )
            .join(UserItemLink, User.id == UserItemLink.user_id, isouter=True)
            .join(Item, UserItemLink.item_id == Item.id, isouter=True)
            .join(Task, User.id == Task.user_id, isouter=True)
            .join(Rating, User.id == Rating.user_id, isouter=True)
            .join(Comment, User.id == Comment.user_id, isouter=True)
            .join(Reaction, User.id == Reaction.user_id, isouter=True)
            .join(UserQuestLink, User.id == UserQuestLink.user_id, isouter=True)
            .join(Quest, UserQuestLink.quest_id == Quest.id, isouter=True)
            .offset(offset)
            .limit(limit)
            .where(User.tribe == user_tribe)
        ).all()

        return self._construct_user_views(user_with_items)

    async def update_user(self, user_id: UUID, user_update: UserUpdate) -> UserView:
        try:
            db_user = self.session.exec(select(User).where(User.id == user_id)).one()
            db_user_data = user_update.model_dump(exclude_unset=True)
            db_user.sqlmodel_update(db_user_data)
            self.session.add(db_user)
            self.session.commit()
            self.session.refresh(db_user)
            logger.info(f"Updated user: {db_user.username}")
            user_with_items = self.session.exec(
                select(User, UserItemLink, Item, UserQuestLink, Quest)
                .join(UserItemLink, User.id == UserItemLink.user_id, isouter=True)
                .join(Item, UserItemLink.item_id == Item.id, isouter=True)
                .join(UserQuestLink, User.id == UserQuestLink.user_id, isouter=True)
                .join(Quest, UserQuestLink.quest_id == Quest.id, isouter=True)
                .where(User.id == db_user.id)
            ).all()
            return self._construct_user_view(user_with_items)
        except NoResultFound:
            raise UserNotFoundError(user_id=user_id)

    async def delete_user(self, user_id: UUID) -> None:
        try:
            db_user = self.session.exec(select(User).where(User.id == user_id)).one()
            self.session.delete(db_user)
            self.session.commit()
            logger.info(f"Deleted user: {db_user.username}")
        except NoResultFound:
            raise UserNotFoundError(user_id=user_id)

    async def update_user_password(self, user_id: UUID, password: str) -> UserView:
        try:
            db_user = self.session.exec(select(User).where(User.id == user_id)).one()
            db_user.password = password
            self.session.add(db_user)
            self.session.commit()
            self.session.refresh(db_user)
            logger.info(f"Updated user password: {db_user.username}")
            user_with_items = self.session.exec(
                select(User, UserItemLink, Item, UserQuestLink, Quest)
                .join(UserItemLink, User.id == UserItemLink.user_id, isouter=True)
                .join(Item, UserItemLink.item_id == Item.id, isouter=True)
                .join(UserQuestLink, User.id == UserQuestLink.user_id, isouter=True)
                .join(Quest, UserQuestLink.quest_id == Quest.id, isouter=True)
                .where(User.id == db_user.id)
            ).all()
            return self._construct_user_view(user_with_items)
        except NoResultFound:
            raise UserNotFoundError(user_id=user_id)

    async def equip_item_to_user(
        self, user_id: UUID, item_id: UUID, equipped: bool
    ) -> UserView:
        try:
            self.session.exec(select(User).where(User.id == user_id)).one()
        except NoResultFound:
            raise UserNotFoundError(user_id=user_id)

        try:
            item_link = self.session.exec(
                select(UserItemLink).where(
                    UserItemLink.user_id == user_id, UserItemLink.item_id == item_id
                )
            ).one()
        except NoResultFound:
            raise ItemLinkToUserNotFoundError(item_id=item_id)

        item_link.equipped = equipped
        self.session.add(item_link)
        self.session.commit()
        self.session.refresh(item_link)

        return await self.get_user_by_id(user_id)

    async def get_user_by_id(self, user_id: UUID) -> UserView:
        user_with_items = self.session.exec(
            select(User, UserItemLink, Item, UserQuestLink, Quest)
            .join(UserItemLink, User.id == UserItemLink.user_id, isouter=True)
            .join(Item, UserItemLink.item_id == Item.id, isouter=True)
            .join(UserQuestLink, User.id == UserQuestLink.user_id, isouter=True)
            .join(Quest, UserQuestLink.quest_id == Quest.id, isouter=True)
            .where(User.id == user_id)
        ).all()

        if not user_with_items:
            raise UserNotFoundError(user_id=user_id)

        return self._construct_user_view(user_with_items)

    def _construct_user_view(self, user_with_items_and_quests) -> UserView:
        user, user_item_link, item, user_quest_link, quest = user_with_items_and_quests[
            0
        ]

        user_items = [
            ItemUserView(
                **item.model_dump(),
                equipped=user_item_link.equipped,
            )
            for _, user_item_link, item, _, _ in user_with_items_and_quests
            if item
        ]

        user_quests = [
            QuestUserView(
                **quest.model_dump(),
                user_id=user.id,
                quest_start=user_quest_link.quest_start,
                quest_end=user_quest_link.quest_end,
                status=user_quest_link.status,
            )
            for _, _, _, user_quest_link, quest in user_with_items_and_quests
            if quest
        ]

        return UserView(
            items=user_items,
            quests=user_quests,
            **user.model_dump(exclude={"password"}),
            tasks=[
                TaskView(
                    **task.model_dump(),
                )
                for task in user.tasks
            ],
            ratings=[
                RatingView(
                    **rating.model_dump(),
                )
                for rating in user.ratings
            ],
            comments=[
                CommentView(
                    **comment.model_dump(),
                )
                for comment in user.comments
            ],
            reactions=[
                ReactionView(
                    **reaction.model_dump(),
                )
                for reaction in user.reactions
            ],
        )

    def _construct_user_views(self, user_with_items_and_quests) -> list[UserView]:
        users = {}
        for (
            user,
            user_item_link,
            item,
            task,
            rating,
            comment,
            reaction,
            user_quest_link,
            quest,
        ) in user_with_items_and_quests:
            if user.id not in users:
                users[user.id] = {
                    "user": user,
                    "items": {},
                    "tasks": {},
                    "ratings": {},
                    "comments": {},
                    "reactions": {},
                    "quests": {},
                }

            if user_item_link and item:
                item_key = (item.id, user.id)
                if item_key not in users[user.id]["items"]:
                    users[user.id]["items"][item_key] = ItemUserView(
                        **item.model_dump(), equipped=user_item_link.equipped
                    )

            if task:
                if task.id not in users[user.id]["tasks"]:
                    users[user.id]["tasks"][task.id] = TaskView(**task.model_dump())

            if rating:
                if rating.id not in users[user.id]["ratings"]:
                    users[user.id]["ratings"][rating.id] = RatingView(
                        **rating.model_dump()
                    )

            if comment:
                if comment.id not in users[user.id]["comments"]:
                    users[user.id]["comments"][comment.id] = CommentView(
                        **comment.model_dump()
                    )

            if reaction:
                if reaction.id not in users[user.id]["reactions"]:
                    users[user.id]["reactions"][reaction.id] = ReactionView(
                        **reaction.model_dump()
                    )

            if user_quest_link and quest:
                quest_key = (quest.id, user.id)
                if quest_key not in users[user.id]["quests"]:
                    users[user.id]["quests"][quest_key] = QuestUserView(
                        quest_start=user_quest_link.quest_start,
                        quest_end=user_quest_link.quest_end,
                        status=user_quest_link.status,
                        **quest.model_dump(),
                    )

        return [
            UserView(
                **user_data["user"].model_dump(exclude={"password"}),
                items=list(user_data["items"].values()),
                tasks=list(user_data["tasks"].values()),
                ratings=list(user_data["ratings"].values()),
                comments=list(user_data["comments"].values()),
                reactions=list(user_data["reactions"].values()),
                quests=list(user_data["quests"].values()),
            )
            for user_data in users.values()
        ]
