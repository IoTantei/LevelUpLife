import uuid
from datetime import datetime
from unittest.mock import AsyncMock
import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from leveluplife.controllers.quest import QuestController
from leveluplife.dependencies import get_quest_controller
from leveluplife.models.error import (
    QuestAlreadyExistsError,
    QuestNotFoundError,
    QuestInUserNotFoundError,
)
from leveluplife.models.quest import Type
from leveluplife.models.table import Quest, User
from leveluplife.models.user import Tribe
from leveluplife.models.view import QuestWithUser


@pytest.mark.asyncio
async def test_create_quest(
    quest_controller: QuestController, app: FastAPI, client: TestClient
) -> None:
    quest_data = {
        "name": "JohnDoe",
        "description": "description test",
        "type": "daily",
        "xp_reward": 100,
    }

    mock_quest = Quest(
        id=uuid.uuid4(),
        created_at=datetime(2020, 1, 1),
        updated_at=datetime(2021, 1, 1),
        deleted_at=None,
        **quest_data,
    )

    def _mock_create_quest():
        quest_controller.create_quest = AsyncMock(return_value=mock_quest)
        return quest_controller

    app.dependency_overrides[get_quest_controller] = _mock_create_quest

    create_quest_response = client.post("/quests", json=quest_data)
    assert create_quest_response.status_code == 201
    actual_response = create_quest_response.json()
    assert actual_response == {
        "id": str(mock_quest.id),
        "created_at": mock_quest.created_at.isoformat(),
        "updated_at": mock_quest.updated_at.isoformat(),
        "deleted_at": None,
        "name": mock_quest.name,
        "description": mock_quest.description,
        "type": mock_quest.type,
        "xp_reward": mock_quest.xp_reward,
    }


@pytest.mark.asyncio
async def test_create_quest_raise_quest_already_exists_error(
    quest_controller: QuestController, app: FastAPI, client: TestClient
):
    quest_data = {
        "name": "JohnDoe",
        "description": "description test",
        "type": "daily",
    }

    def _mock_create_quest():
        quest_controller.create_quest = AsyncMock(
            side_effect=QuestAlreadyExistsError(_name=quest_data["name"])
        )
        return quest_controller

    app.dependency_overrides[get_quest_controller] = _mock_create_quest

    create_quest_response = client.post("/quests", json=quest_data)
    assert create_quest_response.status_code == 409
    assert create_quest_response.json() == {
        "name": "QuestAlreadyExistsError",
        "message": f"Quest with the name {quest_data['name']} already exists.",
        "status_code": 409,
    }


@pytest.mark.asyncio
async def test_get_quests(
    quest_controller: QuestController, client: TestClient, app: FastAPI
) -> None:
    mock_quests = [
        Quest(
            id=uuid.uuid4(),
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2021, 1, 1),
            deleted_at=None,
            name="JohnDoe",
            description="John Doe is going to the supermarket",
            type=Type("daily"),
            xp_reward=100,
        ),
        Quest(
            id=uuid.uuid4(),
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2021, 1, 1),
            deleted_at=None,
            name="JohnDoe2",
            description="John Doe is going to the supermarket",
            type=Type("weekly"),
            xp_reward=100,
        ),
    ]

    def _mock_get_quests():
        quest_controller.get_quests = AsyncMock(return_value=mock_quests)
        return quest_controller

    app.dependency_overrides[get_quest_controller] = _mock_get_quests

    get_quest_response = client.get("/quests")
    assert get_quest_response.status_code == 200
    assert get_quest_response.json() == [
        {
            "id": str(quest.id),
            "created_at": quest.created_at.isoformat(),
            "updated_at": quest.updated_at.isoformat(),
            "deleted_at": None,
            "name": quest.name,
            "description": quest.description,
            "type": quest.type,
            "xp_reward": quest.xp_reward,
        }
        for quest in mock_quests
    ]


@pytest.mark.asyncio
async def test_get_quest_by_id(
    quest_controller: QuestController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_get_quest_by_id():
        quest_controller.get_quest_by_id = AsyncMock(
            return_value=Quest(
                id=_id,
                created_at=datetime(2020, 1, 1),
                updated_at=datetime(2021, 1, 1),
                name="Supermarket",
                description="John Doe is going to the supermarket",
                type=Type("daily"),
                xp_reward=100,
            ),
        )
        return quest_controller

    app.dependency_overrides[get_quest_controller] = _mock_get_quest_by_id
    get_quest_by_id_response = client.get(f"/quests/{_id}")
    assert get_quest_by_id_response.status_code == 200
    assert get_quest_by_id_response.json() == {
        "id": str(_id),
        "created_at": "2020-01-01T00:00:00",
        "updated_at": "2021-01-01T00:00:00",
        "deleted_at": None,
        "name": "Supermarket",
        "description": "John Doe is going to the supermarket",
        "type": "daily",
        "xp_reward": 100,
        "users": [],
    }


@pytest.mark.asyncio
async def test_get_quest_by_id_raise_quest_not_found_error(
    quest_controller: QuestController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_get_quest_by_id():
        quest_controller.get_quest_by_id = AsyncMock(
            side_effect=QuestNotFoundError(quest_id=_id)
        )
        return quest_controller

    app.dependency_overrides[get_quest_controller] = _mock_get_quest_by_id

    get_quest_by_id_response = client.get(f"/quests/{_id}")
    assert get_quest_by_id_response.status_code == 404
    assert get_quest_by_id_response.json() == {
        "message": f"Quest with ID {_id} not found",
        "name": "QuestNotFoundError",
        "status_code": 404,
    }


@pytest.mark.asyncio
async def test_update_quest(
    client: TestClient, app: FastAPI, quest_controller: QuestController
) -> None:
    _id = uuid.uuid4()

    quest_update_data = {
        "name": "JohnDoe",
        "description": "description test",
        "type": "daily",
        "xp_reward": 100,
    }

    updated_quest = Quest(
        id=_id,
        created_at=datetime(2020, 1, 1),
        updated_at=datetime(2021, 1, 1),
        deleted_at=None,
        **quest_update_data,
    )

    def _mock_update_quest():
        quest_controller.update_quest = AsyncMock(return_value=updated_quest)
        return quest_controller

    app.dependency_overrides[get_quest_controller] = _mock_update_quest

    update_quest_response = client.patch(f"/quests/{_id}", json=quest_update_data)
    assert update_quest_response.status_code == 200
    assert update_quest_response.json() == {
        "id": str(_id),
        "created_at": updated_quest.created_at.isoformat(),
        "updated_at": updated_quest.updated_at.isoformat(),
        "deleted_at": None,
        "name": updated_quest.name,
        "description": updated_quest.description,
        "type": updated_quest.type,
        "xp_reward": updated_quest.xp_reward,
    }


@pytest.mark.asyncio
async def test_update_quest_raise_quest_not_found_error(
    quest_controller: QuestController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    quest_update_data = {
        "name": "JohnDoe",
        "description": "description test",
        "type": "daily",
    }

    def _mock_update_quest():
        quest_controller.update_quest = AsyncMock(
            side_effect=QuestNotFoundError(quest_id=_id)
        )
        return quest_controller

    app.dependency_overrides[get_quest_controller] = _mock_update_quest
    update_quest_response = client.patch(f"/quests/{_id}", json=quest_update_data)
    assert update_quest_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_quest(
    quest_controller: QuestController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_delete_quest():
        quest_controller.delete_quest = AsyncMock(return_value=None)
        return quest_controller

    app.dependency_overrides[get_quest_controller] = _mock_delete_quest
    delete_quest_response = client.delete(f"/quests/{_id}")
    assert delete_quest_response.status_code == 204


@pytest.mark.asyncio
async def test_delete_quest_raise_quest_not_found_error(
    quest_controller: QuestController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_delete_quest():
        quest_controller.delete_quest = AsyncMock(
            side_effect=QuestNotFoundError(quest_id=_id)
        )
        return quest_controller

    app.dependency_overrides[get_quest_controller] = _mock_delete_quest
    delete_quest_response = client.delete(f"/quests/{_id}")
    assert delete_quest_response.status_code == 404


@pytest.mark.asyncio
async def test_assign_quest_to_user(
    quest_controller: QuestController, app: FastAPI, client: TestClient
) -> None:
    quest_id = uuid.uuid4()
    user_id = uuid.uuid4()
    user_quest_link_create = {"user_ids": [str(user_id)]}

    def _mock_assign_quest_to_user():
        quest_controller.get_quest_by_id = AsyncMock(
            return_value=Quest(
                id=quest_id,
                name="Supermarket",
                description="John Doe is going to the supermarket",
                type=Type("daily"),
                xp_reward=100,
                created_at=datetime(2020, 1, 1),
                updated_at=datetime(2021, 1, 1),
            )
        )
        quest_controller.assign_quest_to_user = AsyncMock(
            return_value=QuestWithUser(
                id=quest_id,
                created_at=datetime(2020, 1, 1),
                updated_at=datetime(2021, 1, 1),
                deleted_at=None,
                name="Supermarket",
                description="John Doe is going to the supermarket",
                type=Type("daily"),
                xp_reward=100,
                users=[
                    User(
                        id=user_id,
                        username="JohnDoe",
                        created_at=datetime(2020, 1, 1),
                        email="john.doe@test.com",
                        background_image="background_image",
                        biography="biography",
                        profile_picture="profile_picture",
                        tribe=Tribe.NOSFERATI,
                        strength=10,
                        intelligence=10,
                        items=[],
                        agility=10,
                        wise=10,
                        psycho=10,
                        experience=0,
                        tasks=[],
                        quests=[],
                    )
                ],
            )
        )
        return quest_controller

    app.dependency_overrides[get_quest_controller] = _mock_assign_quest_to_user

    assign_quest_response = client.patch(
        f"/quests/{quest_id}/link_user", json=user_quest_link_create
    )

    assert assign_quest_response.status_code == 200
    assert assign_quest_response.json() == {
        "id": str(quest_id),
        "created_at": "2020-01-01T00:00:00",
        "updated_at": "2021-01-01T00:00:00",
        "deleted_at": None,
        "name": "Supermarket",
        "description": "John Doe is going to the supermarket",
        "type": "daily",
        "xp_reward": 100,
        "users": [
            {
                "id": str(user_id),
                "created_at": "2020-01-01T00:00:00",
                "username": "JohnDoe",
                "email": "john.doe@test.com",
                "tribe": "Nosferati",
                "biography": "biography",
                "profile_picture": "profile_picture",
                "background_image": "background_image",
                "strength": 10,
                "intelligence": 10,
                "agility": 10,
                "wise": 10,
                "psycho": 10,
                "experience": 0,
            }
        ],
    }


@pytest.mark.asyncio
async def test_remove_quest_from_user(
    quest_controller: QuestController, app: FastAPI, client: TestClient
) -> None:
    quest_id = uuid.uuid4()
    user_id = uuid.uuid4()

    def _mock_remove_quest_from_user():
        quest_controller.remove_quest_from_user = AsyncMock(return_value=None)
        return quest_controller

    app.dependency_overrides[get_quest_controller] = _mock_remove_quest_from_user

    remove_quest_response = client.delete(f"/quests/{quest_id}/unlink_user/{user_id}")
    assert remove_quest_response.status_code == 204


@pytest.mark.asyncio
async def test_remove_quest_from_user_raise_quest_in_user_not_found_error(
    quest_controller: QuestController, app: FastAPI, client: TestClient
) -> None:
    quest_id = uuid.uuid4()
    user_id = uuid.uuid4()

    def _mock_remove_quest_from_user():
        quest_controller.remove_quest_from_user = AsyncMock(
            side_effect=QuestInUserNotFoundError(quest_id=quest_id, user_id=user_id)
        )
        return quest_controller

    app.dependency_overrides[get_quest_controller] = _mock_remove_quest_from_user

    remove_quest_response = client.delete(f"/quests/{quest_id}/unlink_user/{user_id}")
    assert remove_quest_response.status_code == 404
    assert remove_quest_response.json() == {
        "message": f"Quest: {quest_id} in User: {user_id} not found.",
        "name": "QuestInUserNotFoundError",
        "status_code": 404,
    }
