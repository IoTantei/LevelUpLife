from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends

from leveluplife.auth.utils import get_current_active_user
from leveluplife.controllers.comment import CommentController
from leveluplife.dependencies import get_comment_controller
from leveluplife.models.comment import CommentCreate, CommentUpdate
from leveluplife.models.view import CommentView

router = APIRouter(
    prefix="/comments",
    tags=["comments"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=CommentView, status_code=201)
async def create_comment(
    comment: CommentCreate,
    comment_controller: CommentController = Depends(get_comment_controller),
) -> CommentView:
    return CommentView.model_validate(await comment_controller.create_comment(comment))


@router.get("/", response_model=Sequence[CommentView])
async def get_comments(
    *,
    offset: int = 0,
    comment_controller: CommentController = Depends(get_comment_controller),
) -> Sequence[CommentView]:
    return [
        CommentView.model_validate(comment)
        for comment in await comment_controller.get_comments(offset * 20, 20)
    ]


@router.get("/{comment_id}", response_model=CommentView)
async def get_comment_by_id(
    *,
    comment_id: UUID,
    comment_controller: CommentController = Depends(get_comment_controller),
) -> CommentView:
    return CommentView.model_validate(
        await comment_controller.get_comment_by_id(comment_id)
    )


@router.patch("/{comment_id}", response_model=CommentView)
async def update_comment(
    *,
    comment_id: UUID,
    comment_update: CommentUpdate,
    comment_controller: CommentController = Depends(get_comment_controller),
) -> CommentView:
    return CommentView.model_validate(
        await comment_controller.update_comment(comment_id, comment_update)
    )


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(
    *,
    comment_id: UUID,
    comment_controller: CommentController = Depends(get_comment_controller),
) -> None:
    await comment_controller.delete_comment(comment_id)
