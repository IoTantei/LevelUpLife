import uuid
from uuid import UUID
from datetime import datetime
from unittest.mock import AsyncMock
from leveluplife.dependencies import get_rating_controller
import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient
from leveluplife.controllers.rating import RatingController
from leveluplife.models.error import RatingAlreadyExistsError, RatingNotFoundError
from leveluplife.models.table import Rating, Task, User
from leveluplife.models.user import Tribe


@pytest.mark.asyncio
async def test_create_rating(
    rating_controller: RatingController, app: FastAPI, client: TestClient
) -> None:
    rating_data = {
        "rating": 5,
        "user_id": str(uuid.uuid4()),
        "task_id": str(uuid.uuid4()),
    }

    mock_rating = Rating(
        id=uuid.uuid4(),
        created_at=datetime(2020, 1, 1),
        **rating_data,
    )

    def _mock_create_rating():
        rating_controller.create_rating = AsyncMock(return_value=mock_rating)
        return rating_controller

    app.dependency_overrides[get_rating_controller] = _mock_create_rating

    create_rating_response = client.post("/ratings", json=rating_data)
    assert create_rating_response.status_code == 201
    assert create_rating_response.json() == {
        "id": str(mock_rating.id),
        "created_at": mock_rating.created_at.isoformat(),
        "rating": mock_rating.rating,
        "user_id": str(mock_rating.user_id),
        "task_id": str(mock_rating.task_id),
    }


@pytest.mark.asyncio
async def test_create_rating_raise_rating_already_exists_error(
    rating_controller: RatingController, app: FastAPI, client: TestClient
):
    rating_data = {
        "rating": 5,
        "user_id": str(uuid.uuid4()),
        "task_id": str(uuid.uuid4()),
    }

    def _mock_create_rating():
        rating_controller.create_rating = AsyncMock(
            side_effect=RatingAlreadyExistsError(task_id=UUID(rating_data["task_id"]))
        )
        return rating_controller

    app.dependency_overrides[get_rating_controller] = _mock_create_rating

    create_rating_response = client.post("/ratings", json=rating_data)
    assert create_rating_response.status_code == 409
    assert create_rating_response.json() == {
        "name": "RatingAlreadyExistsError",
        "message": f"Rating for the task {rating_data['task_id']} already exists.",
        "status_code": 409,
    }


@pytest.mark.asyncio
async def test_get_tasks(
    rating_controller: RatingController, client: TestClient, app: FastAPI
) -> None:
    mock_user = User(
        id=uuid.uuid4(),
        username="test_user",
        email="test@gmail.com",
        tribe=Tribe.NEUTRALS,
        created_at=datetime(2020, 1, 1),
        strength=5,
        intelligence=5,
        agility=5,
        wise=5,
        psycho=5,
        experience=0,
    )

    mock_tasks = [
        Task(
            id=uuid.uuid4(),
            created_at=datetime(2020, 1, 1),
            title="Supermarket",
            description="John Doe is going to the supermarket",
            completed=False,
            category="Groceries",
            user_id=mock_user.id,
        ),
        Task(
            id=uuid.uuid4(),
            created_at=datetime(2022, 2, 2),
            title="Video games",
            description="Playing video games",
            completed=True,
            category="Fun",
            user_id=mock_user.id,
        ),
    ]

    mock_ratings = [
        Rating(
            id=uuid.uuid4(),
            created_at=datetime(2020, 1, 1),
            task_id=mock_tasks[0].id,
            user_id=mock_user.id,
            rating=5,
        ),
        Rating(
            id=uuid.uuid4(),
            created_at=datetime(2022, 2, 2),
            task_id=mock_tasks[1].id,
            user_id=mock_user.id,
            rating=5,
        ),
    ]

    def _mock_get_ratings():
        rating_controller.get_ratings = AsyncMock(return_value=mock_ratings)
        return rating_controller

    app.dependency_overrides[get_rating_controller] = _mock_get_ratings

    get_rating_response = client.get("/ratings")
    assert get_rating_response.status_code == 200
    assert get_rating_response.json() == [
        {
            "id": str(rating.id),
            "created_at": rating.created_at.isoformat(),
            "task_id": str(rating.task_id),
            "user_id": str(rating.user_id),
            "rating": rating.rating,
        }
        for rating in mock_ratings
    ]


@pytest.mark.asyncio
async def test_get_rating_by_id(
    rating_controller: RatingController, client: TestClient, app: FastAPI
) -> None:
    mock_user = User(
        id=uuid.uuid4(),
        username="test_user",
        email="test@gmail.com",
        tribe=Tribe.NEUTRALS,
        created_at=datetime(2020, 1, 1),
        strength=5,
        intelligence=5,
        agility=5,
        wise=5,
        psycho=5,
        experience=0,
    )

    mock_task = Task(
        id=uuid.uuid4(),
        created_at=datetime(2020, 1, 1),
        title="Supermarket",
        description="John Doe is going to the supermarket",
        completed=False,
        category="Groceries",
        user_id=mock_user.id,
    )

    mock_rating = Rating(
        id=uuid.uuid4(),
        created_at=datetime(2020, 1, 1),
        task_id=mock_task.id,
        user_id=mock_user.id,
        rating=5,
    )

    def _mock_get_rating_by_id():
        rating_controller.get_rating_by_id = AsyncMock(
            return_value=mock_rating,
        )
        return rating_controller

    app.dependency_overrides[get_rating_controller] = _mock_get_rating_by_id
    get_rating_by_id_response = client.get(f"/ratings/{mock_rating.id}")
    assert get_rating_by_id_response.status_code == 200
    assert get_rating_by_id_response.json() == {
        "id": str(mock_rating.id),
        "created_at": mock_rating.created_at.isoformat(),
        "task_id": str(mock_rating.task_id),
        "user_id": str(mock_rating.user_id),
        "rating": mock_rating.rating,
    }


@pytest.mark.asyncio
async def test_get_rating_by_id_raise_rating_not_found_error(
    rating_controller: RatingController, client: TestClient, app: FastAPI
) -> None:
    mock_rating_id = uuid.uuid4()

    def _mock_get_rating_by_id():
        rating_controller.get_rating_by_id = AsyncMock(
            side_effect=RatingNotFoundError(rating_id=mock_rating_id)
        )
        return rating_controller

    app.dependency_overrides[get_rating_controller] = _mock_get_rating_by_id

    get_rating_by_id_response = client.get(f"/ratings/{mock_rating_id}")
    assert get_rating_by_id_response.status_code == 404
    assert get_rating_by_id_response.json() == {
        "message": f"Rating with ID {mock_rating_id} not found",
        "name": "RatingNotFoundError",
        "status_code": 404,
    }


@pytest.mark.asyncio
async def test_update_rating(
    rating_controller: RatingController, client: TestClient, app: FastAPI
) -> None:
    mock_user = User(
        id=uuid.uuid4(),
        username="test_user",
        email="test@gmail.com",
        tribe=Tribe.NEUTRALS,
        created_at=datetime(2020, 1, 1),
        strength=5,
        intelligence=5,
        agility=5,
        wise=5,
        psycho=5,
        experience=0,
    )

    mock_task = Task(
        id=uuid.uuid4(),
        created_at=datetime(2020, 1, 1),
        title="Supermarket",
        description="John Doe is going to the supermarket",
        completed=False,
        category="Groceries",
        user_id=mock_user.id,
    )

    mock_rating_id = uuid.uuid4()

    rating_update_data = {
        "rating": 3,
    }

    updated_rating = Rating(
        id=mock_rating_id,
        **rating_update_data,
        created_at=datetime(2020, 1, 1),
        task_id=mock_task.id,
        user_id=mock_user.id,
    )

    def _mock_update_rating():
        rating_controller.update_rating = AsyncMock(return_value=updated_rating)
        return rating_controller

    app.dependency_overrides[get_rating_controller] = _mock_update_rating

    update_rating_response = client.patch(
        f"/ratings/{mock_rating_id}", json=rating_update_data
    )
    assert update_rating_response.status_code == 200
    assert update_rating_response.json() == {
        "id": str(updated_rating.id),
        "created_at": updated_rating.created_at.isoformat(),
        "task_id": str(updated_rating.task_id),
        "user_id": str(updated_rating.user_id),
        "rating": updated_rating.rating,
    }


@pytest.mark.asyncio
async def test_update_rating_raise_rating_not_found_error(
    rating_controller: RatingController, client: TestClient, app: FastAPI
) -> None:
    mock_rating_id = uuid.uuid4()

    rating_update_data = {
        "rating": 3,
    }

    def _mock_update_rating():
        rating_controller.update_rating = AsyncMock(
            side_effect=RatingNotFoundError(rating_id=mock_rating_id)
        )
        return rating_controller

    app.dependency_overrides[get_rating_controller] = _mock_update_rating

    update_rating_response = client.patch(
        f"/ratings/{mock_rating_id}", json=rating_update_data
    )
    assert update_rating_response.status_code == 404
    assert update_rating_response.json() == {
        "message": f"Rating with ID {mock_rating_id} not found",
        "name": "RatingNotFoundError",
        "status_code": 404,
    }


@pytest.mark.asyncio
async def test_delete_rating(
    rating_controller: RatingController, client: TestClient, app: FastAPI
) -> None:
    mock_rating_id = uuid.uuid4()

    def _mock_delete_rating():
        rating_controller.delete_rating = AsyncMock(return_value=None)
        return rating_controller

    app.dependency_overrides[get_rating_controller] = _mock_delete_rating
    delete_rating_response = client.delete(f"/ratings/{mock_rating_id}")
    assert delete_rating_response.status_code == 204


@pytest.mark.asyncio
async def test_delete_rating_raise_rating_not_found_error(
    rating_controller: RatingController, client: TestClient, app: FastAPI
) -> None:
    mock_rating_id = uuid.uuid4()

    def _mock_delete_rating():
        rating_controller.delete_rating = AsyncMock(
            side_effect=RatingNotFoundError(rating_id=mock_rating_id)
        )
        return rating_controller

    app.dependency_overrides[get_rating_controller] = _mock_delete_rating

    delete_rating_response = client.delete(f"/ratings/{mock_rating_id}")
    assert delete_rating_response.status_code == 404
    assert delete_rating_response.json() == {
        "message": f"Rating with ID {mock_rating_id} not found",
        "name": "RatingNotFoundError",
        "status_code": 404,
    }
