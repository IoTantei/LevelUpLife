from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends

from leveluplife.auth.utils import get_current_active_user
from leveluplife.controllers.user import UserController
from leveluplife.dependencies import get_user_controller
from leveluplife.models.table import User
from leveluplife.models.user import UserCreate, UserUpdate, UserUpdatePassword, Tribe
from leveluplife.models.view import UserView

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.post("/", response_model=UserView, status_code=201)
async def create_user(
    *, user: UserCreate, user_controller: UserController = Depends(get_user_controller)
) -> UserView:
    return UserView.model_validate(await user_controller.create_user(user))


@router.get("/", response_model=list[UserView])
async def get_users(
    *,
    offset: int = 0,
    user_controller: UserController = Depends(get_user_controller),
    current_user: User = Depends(get_current_active_user)
) -> list[UserView]:
    return [
        UserView.model_validate(user)
        for user in await user_controller.get_users(offset * 20, 20)
    ]


@router.get("/{user_id}", response_model=UserView)
async def get_user_by_id(
    *,
    user_id: UUID,
    user_controller: UserController = Depends(get_user_controller),
    current_user: User = Depends(get_current_active_user)
) -> UserView:
    return UserView.model_validate(await user_controller.get_user_by_id(user_id))


@router.get("/type/username", response_model=UserView)
async def get_user_by_username(
    *,
    user_username: str,
    user_controller: UserController = Depends(get_user_controller),
    current_user: User = Depends(get_current_active_user)
) -> UserView:
    return UserView.model_validate(
        await user_controller.get_user_by_username(user_username)
    )


@router.get("/type/email", response_model=UserView)
async def get_user_by_email(
    *,
    user_email: str,
    user_controller: UserController = Depends(get_user_controller),
    current_user: User = Depends(get_current_active_user)
) -> UserView:
    return UserView.model_validate(await user_controller.get_user_by_email(user_email))


@router.get("/type/tribe", response_model=list[UserView])
async def get_users_by_tribe(
    *,
    offset: int = 0,
    user_tribe: Tribe,
    user_controller: UserController = Depends(get_user_controller),
    current_user: User = Depends(get_current_active_user)
) -> list[UserView]:
    users = await user_controller.get_users_by_tribe(user_tribe, offset * 20, 20)
    return [UserView.model_validate(user) for user in users]


@router.patch("/{user_id}", response_model=UserView)
async def update_user(
    *,
    user_id: UUID,
    user_update: UserUpdate,
    user_controller: UserController = Depends(get_user_controller),
    current_user: User = Depends(get_current_active_user)
) -> UserView:
    return UserView.model_validate(
        await user_controller.update_user(user_id, user_update)
    )


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    *,
    user_id: UUID,
    user_controller: UserController = Depends(get_user_controller),
    current_user: User = Depends(get_current_active_user)
) -> None:
    await user_controller.delete_user(user_id)


@router.patch("/{user_id}/password", response_model=UserView)
async def update_user_password(
    *,
    user_id: UUID,
    user_update_password: UserUpdatePassword,
    user_controller: UserController = Depends(get_user_controller),
    current_user: User = Depends(get_current_active_user)
) -> UserView:
    return UserView.model_validate(
        await user_controller.update_user_password(
            user_id, user_update_password.password
        )
    )


@router.post("/{user_id}/items/{item_id}/equip", response_model=UserView)
async def equip_item_to_user(
    user_id: UUID,
    item_id: UUID,
    equipped: bool,
    user_controller: UserController = Depends(get_user_controller),
    current_user: User = Depends(get_current_active_user),
) -> UserView:
    return UserView.model_validate(
        await user_controller.equip_item_to_user(user_id, item_id, equipped)
    )
