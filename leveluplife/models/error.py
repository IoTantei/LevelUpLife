from uuid import UUID


class BaseError(Exception):
    def __init__(self, name: str, message: str, status_code: int):
        self.name = name
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UserEmailAlreadyExistsError(BaseError):
    def __init__(
        self,
        email: str,
        status_code: int = 409,
        name: str = "UserEmailAlreadyExistsError",
    ):
        self.name = name
        self.message = f"User with the email {email} already exists."
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class UserUsernameAlreadyExistsError(BaseError):
    def __init__(
        self,
        username: str,
        status_code: int = 409,
        name: str = "UserUsernameAlreadyExistsError",
    ):
        self.name = name
        self.message = f"User with the username {username} already exists."
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class UserNotFoundError(BaseError):
    def __init__(
        self, user_id: UUID, status_code: int = 404, name: str = "UserNotFoundError"
    ):
        self.name = name
        self.message = f"User with ID {user_id} not found"
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class UserUsernameNotFoundError(BaseError):
    def __init__(
        self,
        user_username: str,
        status_code: int = 404,
        name: str = "UserUsernameNotFoundError",
    ):
        self.name = name
        self.message = f"User with username {user_username} not found"
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class UserEmailNotFoundError(BaseError):
    def __init__(
        self,
        user_email: str,
        status_code: int = 404,
        name: str = "UserEmailNotFoundError",
    ):
        self.name = name
        self.message = f"User with email {user_email} not found"
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class TaskAlreadyExistsError(BaseError):
    def __init__(
        self, title: str, status_code: int = 409, name: str = "TaskAlreadyExistsError"
    ):
        self.name = name
        self.message = f"Task with the title {title} already exists."
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class TaskNotFoundError(BaseError):
    def __init__(
        self, task_id: UUID, status_code: int = 404, name: str = "TaskNotFoundError"
    ):
        self.name = name
        self.message = f"Task with ID {task_id} not found"
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class TaskTitleNotFoundError(BaseError):
    def __init__(
        self,
        task_title: str,
        status_code: int = 404,
        name: str = "TaskTitleNotFoundError",
    ):
        self.name = name
        self.message = f"Task with title {task_title} not found"
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class ItemAlreadyExistsError(BaseError):
    def __init__(
        self, _name: str, status_code: int = 409, name: str = "ItemAlreadyExistsError"
    ):
        self.name = name
        self.message = f"Item with the name {_name} already exists."
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class ItemNotFoundError(BaseError):
    def __init__(
        self, item_id: UUID, status_code: int = 404, name: str = "ItemNotFoundError"
    ):
        self.name = name
        self.message = f"Item with ID {item_id} not found"
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class ItemNameNotFoundError(BaseError):
    def __init__(
        self,
        item_name: str,
        status_code: int = 404,
        name: str = "ItemNameNotFoundError",
    ):
        self.name = name
        self.message = f"Item with name {item_name} not found"
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class ItemAlreadyInUserError(BaseError):
    def __init__(
        self,
        username: str,
        item_id: UUID,
        status_code: int = 409,
        name: str = "ItemAlreadyInUserError",
    ):
        self.name = name
        self.message = (
            f"User {username} already have the item {item_id} in his/her inventory."
        )
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class ItemLinkToUserNotFoundError(BaseError):
    def __init__(
        self,
        item_id: UUID,
        status_code: int = 404,
        name: str = "ItemLinkToUserNotFoundError",
    ):
        self.name = name
        self.message = f"ItemLinkToUserNotFoundError with Item ID {item_id} not found in the inventory."
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class ItemInUserNotFoundError(BaseError):
    def __init__(
        self,
        item_id: UUID,
        user_id: UUID,
        status_code: int = 404,
        name: str = "ItemInUserNotFoundError",
    ):
        self.name = name
        self.message = f"Item: {item_id} in User: {user_id} not found."
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class RatingAlreadyExistsError(BaseError):
    def __init__(
        self,
        task_id: UUID,
        status_code: int = 409,
        name: str = "RatingAlreadyExistsError",
    ):
        self.name = name
        self.message = f"Rating for the task {task_id} already exists."
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class RatingNotFoundError(BaseError):
    def __init__(
        self, rating_id: UUID, status_code: int = 404, name: str = "RatingNotFoundError"
    ):
        self.name = name
        self.message = f"Rating with ID {rating_id} not found"
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class CommentAlreadyExistsError(BaseError):
    def __init__(
        self,
        task_id: UUID,
        status_code: int = 409,
        name: str = "CommentAlreadyExistsError",
    ):
        self.name = name
        self.message = f"Comment for the task {task_id} already exists."
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class CommentNotFoundError(BaseError):
    def __init__(
        self,
        comment_id: UUID,
        status_code: int = 404,
        name: str = "CommentNotFoundError",
    ):
        self.name = name
        self.message = f"Comment with ID {comment_id} not found"
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class ReactionAlreadyExistsError(BaseError):
    def __init__(
        self,
        task_id: UUID,
        status_code: int = 409,
        name: str = "ReactionAlreadyExistsError",
    ):
        self.name = name
        self.message = f"Reaction for the task {task_id} already exists."
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class ReactionNotFoundError(BaseError):
    def __init__(
        self,
        reaction_id: UUID,
        status_code: int = 404,
        name: str = "ReactionNotFoundError",
    ):
        self.name = name
        self.message = f"Reaction with ID {reaction_id} not found"
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class QuestAlreadyExistsError(BaseError):
    def __init__(
        self, _name: str, status_code: int = 409, name: str = "QuestAlreadyExistsError"
    ):
        self.name = name
        self.message = f"Quest with the name {_name} already exists."
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class QuestNotFoundError(BaseError):
    def __init__(
        self, quest_id: UUID, status_code: int = 404, name: str = "QuestNotFoundError"
    ):
        self.name = name
        self.message = f"Quest with ID {quest_id} not found"
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class QuestAlreadyInUserError(BaseError):
    def __init__(
        self,
        username: str,
        quest_id: UUID,
        status_code: int = 409,
        name: str = "QuestAlreadyInUserError",
    ):
        self.name = name
        self.message = (
            f"User {username} already have the quest {quest_id} in his/her account."
        )
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class QuestLinkToUserNotFoundError(BaseError):
    def __init__(
        self,
        quest_id: UUID,
        status_code: int = 404,
        name: str = "QuestLinkToUserNotFoundError",
    ):
        self.name = name
        self.message = f"ItemLinkToUserNotFoundError with Item ID {quest_id} not found in the inventory."
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )


class QuestInUserNotFoundError(BaseError):
    def __init__(
        self,
        quest_id: UUID,
        user_id: UUID,
        status_code: int = 404,
        name: str = "QuestInUserNotFoundError",
    ):
        self.name = name
        self.message = f"Quest: {quest_id} in User: {user_id} not found."
        self.status_code = status_code
        super().__init__(
            name=self.name, message=self.message, status_code=self.status_code
        )
