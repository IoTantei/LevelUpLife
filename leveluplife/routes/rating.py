from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends

from leveluplife.auth.utils import get_current_active_user
from leveluplife.controllers.rating import RatingController
from leveluplife.dependencies import get_rating_controller
from leveluplife.models.rating import RatingCreate, RatingUpdate
from leveluplife.models.view import RatingView

router = APIRouter(
    prefix="/ratings",
    tags=["ratings"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=RatingView, status_code=201)
async def create_rating(
    rating: RatingCreate,
    rating_controller: RatingController = Depends(get_rating_controller),
) -> RatingView:
    return RatingView.model_validate(await rating_controller.create_rating(rating))


@router.get("/", response_model=Sequence[RatingView])
async def get_ratings(
    *,
    offset: int = 0,
    rating_controller: RatingController = Depends(get_rating_controller),
) -> Sequence[RatingView]:
    return [
        RatingView.model_validate(rating)
        for rating in await rating_controller.get_ratings(offset * 20, 20)
    ]


@router.get("/{rating_id}", response_model=RatingView)
async def get_rating_by_id(
    *,
    rating_id: UUID,
    rating_controller: RatingController = Depends(get_rating_controller),
) -> RatingView:
    return RatingView.model_validate(
        await rating_controller.get_rating_by_id(rating_id)
    )


@router.patch("/{rating_id}", response_model=RatingView)
async def update_rating(
    *,
    rating_id: UUID,
    rating_update: RatingUpdate,
    rating_controller: RatingController = Depends(get_rating_controller),
) -> RatingView:
    return RatingView.model_validate(
        await rating_controller.update_rating(rating_id, rating_update)
    )


@router.delete("/{rating_id}", status_code=204)
async def delete_rating(
    *,
    rating_id: UUID,
    rating_controller: RatingController = Depends(get_rating_controller),
) -> None:
    await rating_controller.delete_rating(rating_id)
