import uuid
from datetime import datetime
from unittest.mock import AsyncMock
from uuid import UUID
import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from leveluplife.controllers.reaction import ReactionController
from leveluplife.dependencies import get_reaction_controller
from leveluplife.models.error import ReactionAlreadyExistsError, ReactionNotFoundError
from leveluplife.models.reaction import ReactionType
from leveluplife.models.table import Reaction, User, Task
from leveluplife.models.user import Tribe


@pytest.mark.asyncio
async def test_create_comment(
    reaction_controller: ReactionController, app: FastAPI, client: TestClient
) -> None:
    reaction_data = {
        "reaction": "🥰",
        "user_id": str(uuid.uuid4()),
        "task_id": str(uuid.uuid4()),
    }

    mock_reaction = Reaction(
        id=uuid.uuid4(),
        created_at=datetime(2020, 1, 1),
        updated_at=datetime(2021, 1, 1),
        deleted_at=None,
        reaction=ReactionType(reaction_data["reaction"]),
        **{k: v for k, v in reaction_data.items() if k != "reaction"},
    )

    def _mock_create_reaction():
        reaction_controller.create_reaction = AsyncMock(return_value=mock_reaction)
        return reaction_controller

    app.dependency_overrides[get_reaction_controller] = _mock_create_reaction

    create_reaction_response = client.post("/reactions", json=reaction_data)
    assert create_reaction_response.status_code == 201
    assert create_reaction_response.json() == {
        "id": str(mock_reaction.id),
        "created_at": mock_reaction.created_at.isoformat(),
        "updated_at": mock_reaction.updated_at.isoformat(),
        "deleted_at": None,
        "reaction": mock_reaction.reaction,
        "user_id": str(mock_reaction.user_id),
        "task_id": str(mock_reaction.task_id),
    }


@pytest.mark.asyncio
async def test_create_reaction_raise_reaction_already_exists_error(
    reaction_controller: ReactionController, app: FastAPI, client: TestClient
):
    reaction_data = {
        "reaction": "🥰",
        "user_id": str(uuid.uuid4()),
        "task_id": str(uuid.uuid4()),
    }

    def _mock_create_reaction():
        reaction_controller.create_reaction = AsyncMock(
            side_effect=ReactionAlreadyExistsError(
                task_id=UUID(reaction_data["task_id"])
            )
        )
        return reaction_controller

    app.dependency_overrides[get_reaction_controller] = _mock_create_reaction

    create_reaction_response = client.post("/reactions", json=reaction_data)
    assert create_reaction_response.status_code == 409
    assert create_reaction_response.json() == {
        "name": "ReactionAlreadyExistsError",
        "message": f"Reaction for the task {reaction_data['task_id']} already exists.",
        "status_code": 409,
    }


@pytest.mark.asyncio
async def test_get_reactions(
    reaction_controller: ReactionController, client: TestClient, app: FastAPI
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

    mock_reactions = [
        Reaction(
            id=uuid.uuid4(),
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2021, 1, 1),
            deleted_at=None,
            task_id=mock_tasks[0].id,
            user_id=mock_user.id,
            reaction=ReactionType("🥰"),
        ),
        Reaction(
            id=uuid.uuid4(),
            created_at=datetime(2022, 2, 2),
            updated_at=datetime(2021, 1, 1),
            deleted_at=None,
            task_id=mock_tasks[1].id,
            user_id=mock_user.id,
            reaction=ReactionType("😞"),
        ),
    ]

    def _mock_get_reactions():
        reaction_controller.get_reactions = AsyncMock(return_value=mock_reactions)
        return reaction_controller

    app.dependency_overrides[get_reaction_controller] = _mock_get_reactions

    get_reaction_response = client.get("/reactions")
    assert get_reaction_response.status_code == 200
    assert get_reaction_response.json() == [
        {
            "id": str(reaction.id),
            "created_at": reaction.created_at.isoformat(),
            "updated_at": reaction.updated_at.isoformat(),
            "deleted_at": None,
            "task_id": str(reaction.task_id),
            "user_id": str(reaction.user_id),
            "reaction": reaction.reaction,
        }
        for reaction in mock_reactions
    ]


@pytest.mark.asyncio
async def test_get_reaction_by_id(
    reaction_controller: ReactionController, client: TestClient, app: FastAPI
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

    mock_reaction = Reaction(
        id=uuid.uuid4(),
        created_at=datetime(2020, 1, 1),
        updated_at=datetime(2021, 1, 1),
        deleted_at=None,
        task_id=mock_task.id,
        user_id=mock_user.id,
        reaction=ReactionType("🥰"),
    )

    def _mock_get_reaction_by_id():
        reaction_controller.get_reaction_by_id = AsyncMock(
            return_value=mock_reaction,
        )
        return reaction_controller

    app.dependency_overrides[get_reaction_controller] = _mock_get_reaction_by_id
    get_reaction_by_id_response = client.get(f"/reactions/{mock_reaction.id}")
    assert get_reaction_by_id_response.status_code == 200
    assert get_reaction_by_id_response.json() == {
        "id": str(mock_reaction.id),
        "created_at": mock_reaction.created_at.isoformat(),
        "updated_at": mock_reaction.updated_at.isoformat(),
        "deleted_at": None,
        "task_id": str(mock_reaction.task_id),
        "user_id": str(mock_reaction.user_id),
        "reaction": mock_reaction.reaction,
    }


@pytest.mark.asyncio
async def test_get_reaction_by_id_raise_reaction_not_found_error(
    reaction_controller: ReactionController, client: TestClient, app: FastAPI
) -> None:
    mock_reaction_id = uuid.uuid4()

    def _mock_get_reaction_by_id():
        reaction_controller.get_reaction_by_id = AsyncMock(
            side_effect=ReactionNotFoundError(reaction_id=mock_reaction_id)
        )
        return reaction_controller

    app.dependency_overrides[get_reaction_controller] = _mock_get_reaction_by_id

    get_reaction_by_id_response = client.get(f"/reactions/{mock_reaction_id}")
    assert get_reaction_by_id_response.status_code == 404
    assert get_reaction_by_id_response.json() == {
        "message": f"Reaction with ID {mock_reaction_id} not found",
        "name": "ReactionNotFoundError",
        "status_code": 404,
    }


@pytest.mark.asyncio
async def test_update_reaction(
    reaction_controller: ReactionController, client: TestClient, app: FastAPI
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

    mock_reaction_id = uuid.uuid4()

    reaction_update_data = {
        "reaction": "🥰",
    }

    updated_reaction = Reaction(
        id=mock_reaction_id,
        created_at=datetime(2020, 1, 1),
        updated_at=datetime(2021, 1, 1),
        deleted_at=None,
        task_id=mock_task.id,
        user_id=mock_user.id,
        reaction=ReactionType(reaction_update_data["reaction"]),
        **{k: v for k, v in reaction_update_data.items() if k != "reaction"},
    )

    def _mock_update_reaction():
        reaction_controller.update_reaction = AsyncMock(return_value=updated_reaction)
        return reaction_controller

    app.dependency_overrides[get_reaction_controller] = _mock_update_reaction

    update_reaction_response = client.patch(
        f"/reactions/{mock_reaction_id}", json=reaction_update_data
    )
    assert update_reaction_response.status_code == 200
    assert update_reaction_response.json() == {
        "id": str(updated_reaction.id),
        "created_at": updated_reaction.created_at.isoformat(),
        "updated_at": updated_reaction.updated_at.isoformat(),
        "deleted_at": None,
        "task_id": str(updated_reaction.task_id),
        "user_id": str(updated_reaction.user_id),
        "reaction": updated_reaction.reaction,
    }


@pytest.mark.asyncio
async def test_update_reaction_raise_reaction_not_found_error(
    reaction_controller: ReactionController, client: TestClient, app: FastAPI
) -> None:
    mock_reaction_id = uuid.uuid4()

    reaction_update_data = {
        "reaction": "🥰",
    }

    def _mock_update_reaction():
        reaction_controller.update_reaction = AsyncMock(
            side_effect=ReactionNotFoundError(reaction_id=mock_reaction_id)
        )
        return reaction_controller

    app.dependency_overrides[get_reaction_controller] = _mock_update_reaction

    update_reaction_response = client.patch(
        f"/reactions/{mock_reaction_id}", json=reaction_update_data
    )
    assert update_reaction_response.status_code == 404
    assert update_reaction_response.json() == {
        "message": f"Reaction with ID {mock_reaction_id} not found",
        "name": "ReactionNotFoundError",
        "status_code": 404,
    }


@pytest.mark.asyncio
async def test_delete_reaction(
    reaction_controller: ReactionController, client: TestClient, app: FastAPI
) -> None:
    mock_reaction_id = uuid.uuid4()

    def _mock_delete_reaction():
        reaction_controller.delete_reaction = AsyncMock(return_value=None)
        return reaction_controller

    app.dependency_overrides[get_reaction_controller] = _mock_delete_reaction
    delete_reaction_response = client.delete(f"/reactions/{mock_reaction_id}")
    assert delete_reaction_response.status_code == 204


@pytest.mark.asyncio
async def test_delete_reaction_raise_reaction_not_found_error(
    reaction_controller: ReactionController, client: TestClient, app: FastAPI
) -> None:
    mock_reaction_id = uuid.uuid4()

    def _mock_delete_reaction():
        reaction_controller.delete_reaction = AsyncMock(
            side_effect=ReactionNotFoundError(reaction_id=mock_reaction_id)
        )
        return reaction_controller

    app.dependency_overrides[get_reaction_controller] = _mock_delete_reaction

    delete_reaction_response = client.delete(f"/reactions/{mock_reaction_id}")
    assert delete_reaction_response.status_code == 404
    assert delete_reaction_response.json() == {
        "message": f"Reaction with ID {mock_reaction_id} not found",
        "name": "ReactionNotFoundError",
        "status_code": 404,
    }
