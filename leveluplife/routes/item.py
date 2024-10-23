from typing import Sequence
from uuid import UUID
from fastapi import APIRouter, Depends

from leveluplife.auth.utils import get_current_active_user
from leveluplife.controllers.item import ItemController
from leveluplife.dependencies import get_item_controller
from leveluplife.models.item import ItemCreate, ItemUpdate
from leveluplife.models.relationship import UserItemLinkCreate
from leveluplife.models.view import ItemView, ItemWithUser

router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=ItemView, status_code=201)
async def create_item(
    item: ItemCreate, item_controller: ItemController = Depends(get_item_controller)
) -> ItemView:
    return ItemView.model_validate(await item_controller.create_item(item))


@router.patch("/{item_id}", response_model=ItemView)
async def update_item(
    *,
    item_id: UUID,
    item_update: ItemUpdate,
    item_controller: ItemController = Depends(get_item_controller),
) -> ItemView:
    return ItemView.model_validate(
        await item_controller.update_item(item_id, item_update)
    )


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    *, item_id: UUID, item_controller: ItemController = Depends(get_item_controller)
) -> None:
    await item_controller.delete_item(item_id)


@router.get("/", response_model=Sequence[ItemView])
async def get_items(
    *, offset: int = 0, item_controller: ItemController = Depends(get_item_controller)
) -> Sequence[ItemView]:
    return [
        ItemView.model_validate(item)
        for item in await item_controller.get_items(offset * 20, 20)
    ]


@router.get("/{item_id}", response_model=ItemWithUser)
async def get_item_by_id(
    *, item_id: UUID, item_controller: ItemController = Depends(get_item_controller)
) -> ItemWithUser:
    return ItemWithUser.model_validate(await item_controller.get_item_by_id(item_id))


@router.get("/type/name", response_model=ItemView)
async def get_item_by_name(
    *, item_name: str, item_controller: ItemController = Depends(get_item_controller)
) -> ItemView:
    return ItemView.model_validate(await item_controller.get_item_by_name(item_name))


@router.patch("/{item_id}/link_user", response_model=ItemWithUser, status_code=200)
async def give_item_to_user(
    *,
    item_id: UUID,
    user_item_link_create: UserItemLinkCreate,
    item_controller: ItemController = Depends(get_item_controller),
) -> ItemWithUser:
    return ItemWithUser.model_validate(
        await item_controller.give_item_to_user(item_id, user_item_link_create)
    )


@router.delete("/{item_id}/unlink_user/{user_id}", status_code=204)
async def remove_item_from_user(
    *,
    item_id: UUID,
    user_id: UUID,
    item_controller: ItemController = Depends(get_item_controller),
) -> None:
    await item_controller.remove_item_from_user(item_id, user_id)
