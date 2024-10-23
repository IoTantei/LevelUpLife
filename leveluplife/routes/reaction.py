from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends

from leveluplife.auth.utils import get_current_active_user
from leveluplife.controllers.reaction import ReactionController
from leveluplife.dependencies import get_reaction_controller
from leveluplife.models.reaction import ReactionCreate, ReactionUpdate
from leveluplife.models.view import ReactionView

router = APIRouter(
    prefix="/reactions",
    tags=["reactions"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=ReactionView, status_code=201)
async def create_reaction(
    reaction: ReactionCreate,
    reaction_controller: ReactionController = Depends(get_reaction_controller),
) -> ReactionView:
    return ReactionView.model_validate(
        await reaction_controller.create_reaction(reaction)
    )


@router.get("/", response_model=Sequence[ReactionView])
async def get_reactions(
    *,
    offset: int = 0,
    reaction_controller: ReactionController = Depends(get_reaction_controller),
) -> Sequence[ReactionView]:
    return [
        ReactionView.model_validate(reaction)
        for reaction in await reaction_controller.get_reactions(offset * 20, 20)
    ]


@router.get("/{reaction_id}", response_model=ReactionView)
async def get_reaction_by_id(
    *,
    reaction_id: UUID,
    reaction_controller: ReactionController = Depends(get_reaction_controller),
) -> ReactionView:
    return ReactionView.model_validate(
        await reaction_controller.get_reaction_by_id(reaction_id)
    )


@router.patch("/{reaction_id}", response_model=ReactionView)
async def update_reaction(
    *,
    reaction_id: UUID,
    reaction_update: ReactionUpdate,
    reaction_controller: ReactionController = Depends(get_reaction_controller),
) -> ReactionView:
    return ReactionView.model_validate(
        await reaction_controller.update_reaction(reaction_id, reaction_update)
    )


@router.delete("/{reaction_id}", status_code=204)
async def delete_reaction(
    *,
    reaction_id: UUID,
    reaction_controller: ReactionController = Depends(get_reaction_controller),
) -> None:
    await reaction_controller.delete_reaction(reaction_id)
