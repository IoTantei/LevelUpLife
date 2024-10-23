import uuid
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from leveluplife.controllers.task import TaskController
from leveluplife.dependencies import get_task_controller
from leveluplife.models.error import (
    TaskAlreadyExistsError,
    TaskNotFoundError,
    TaskTitleNotFoundError,
)
from leveluplife.models.table import Task, User
from leveluplife.models.user import Tribe


@pytest.mark.asyncio
async def test_create_task(
    task_controller: TaskController, app: FastAPI, client: TestClient
) -> None:
    task_data = {
        "title": "Supermarket",
        "description": "John Doe is going to the supermarket",
        "completed": "False",
        "category": "Groceries",
        "user_id": str(uuid.uuid4()),
    }

    mock_task = Task(
        id=uuid.uuid4(),
        created_at=datetime(2020, 1, 1),
        **task_data,
    )

    def _mock_create_task():
        task_controller.create_task = AsyncMock(return_value=mock_task)
        return task_controller

    app.dependency_overrides[get_task_controller] = _mock_create_task

    create_task_response = client.post("/tasks", json=task_data)
    assert create_task_response.status_code == 201
    assert create_task_response.json() == {
        "id": str(mock_task.id),
        "created_at": mock_task.created_at.isoformat(),
        "title": mock_task.title,
        "description": mock_task.description,
        "completed": mock_task.completed,
        "category": mock_task.category,
        "user_id": str(mock_task.user_id),
    }


@pytest.mark.asyncio
async def test_create_task_raise_task_already_exists_error(
    task_controller: TaskController, client: TestClient, app: FastAPI
) -> None:
    task_data = {
        "title": "Supermarket",
        "description": "John Doe is going to the supermarket",
        "completed": "False",
        "category": "Groceries",
        "user_id": str(uuid.uuid4()),
    }

    def _mock_create_task():
        task_controller.create_task = AsyncMock(
            side_effect=TaskAlreadyExistsError(title=task_data["title"])
        )
        return task_controller

    app.dependency_overrides[get_task_controller] = _mock_create_task

    create_task_response = client.post("/tasks", json=task_data)
    assert create_task_response.status_code == 409
    assert create_task_response.json() == {
        "name": "TaskAlreadyExistsError",
        "message": f"Task with the title {task_data['title']} already exists.",
        "status_code": 409,
    }


@pytest.mark.asyncio
async def test_get_tasks(
    task_controller: TaskController, client: TestClient, app: FastAPI
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

    def _mock_get_tasks():
        task_controller.get_tasks = AsyncMock(return_value=mock_tasks)
        return task_controller

    app.dependency_overrides[get_task_controller] = _mock_get_tasks

    get_task_response = client.get("/tasks")
    assert get_task_response.status_code == 200
    assert get_task_response.json() == [
        {
            "id": str(task.id),
            "created_at": task.created_at.isoformat(),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "category": task.category,
            "user_id": str(task.user_id),
        }
        for task in mock_tasks
    ]


@pytest.mark.asyncio
async def test_get_task_by_id(
    task_controller: TaskController, client: TestClient, app: FastAPI
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

    _id = uuid.uuid4()

    def _mock_get_task_by_id():
        task_controller.get_task_by_id = AsyncMock(
            return_value=Task(
                id=_id,
                created_at=datetime(2020, 1, 1),
                title="Supermarket",
                description="John Doe is going to the supermarket",
                completed=False,
                category="Groceries",
                user_id=mock_user.id,
            ),
        )
        return task_controller

    app.dependency_overrides[get_task_controller] = _mock_get_task_by_id
    get_task_by_id_response = client.get(f"/tasks/{_id}")
    assert get_task_by_id_response.status_code == 200
    assert get_task_by_id_response.json() == {
        "id": str(_id),
        "created_at": "2020-01-01T00:00:00",
        "title": "Supermarket",
        "description": "John Doe is going to the supermarket",
        "completed": False,
        "category": "Groceries",
        "user_id": str(mock_user.id),
    }


@pytest.mark.asyncio
async def test_get_task_by_id_raise_task_not_found_error(
    task_controller: TaskController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_get_task_by_id():
        task_controller.get_task_by_id = AsyncMock(
            side_effect=TaskNotFoundError(task_id=_id)
        )
        return task_controller

    app.dependency_overrides[get_task_controller] = _mock_get_task_by_id

    get_task_by_id_response = client.get(f"/tasks/{_id}")
    assert get_task_by_id_response.status_code == 404
    assert get_task_by_id_response.json() == {
        "message": f"Task with ID {_id} not found",
        "name": "TaskNotFoundError",
        "status_code": 404,
    }


@pytest.mark.asyncio
async def test_get_task_by_title(
    task_controller: TaskController, client: TestClient, app: FastAPI
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

    _id = uuid.uuid4()

    def _mock_get_task_by_title():
        task_controller.get_task_by_title = AsyncMock(
            return_value=Task(
                id=_id,
                created_at=datetime(2020, 1, 1),
                title="Supermarket",
                description="John Doe is going to the supermarket",
                completed=False,
                category="Groceries",
                user_id=mock_user.id,
            ),
        )
        return task_controller

    app.dependency_overrides[get_task_controller] = _mock_get_task_by_title
    get_task_by_title_response = client.get("/tasks/type/title?task_title=Supermarket")
    assert get_task_by_title_response.status_code == 200
    assert get_task_by_title_response.json() == {
        "id": str(_id),
        "created_at": "2020-01-01T00:00:00",
        "title": "Supermarket",
        "description": "John Doe is going to the supermarket",
        "completed": False,
        "category": "Groceries",
        "user_id": str(mock_user.id),
    }


@pytest.mark.asyncio
async def test_get_task_by_title_raise_task_title_not_found_error(
    task_controller: TaskController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_get_task_by_title():
        task_controller.get_task_by_title = AsyncMock(
            side_effect=TaskTitleNotFoundError(task_title="Supermarket")
        )
        return task_controller

    app.dependency_overrides[get_task_controller] = _mock_get_task_by_title

    get_task_by_id_response = client.get("/tasks/type/title?task_title=Supermarket")
    assert get_task_by_id_response.status_code == 404
    assert get_task_by_id_response.json() == {
        "message": "Task with title Supermarket not found",
        "name": "TaskTitleNotFoundError",
        "status_code": 404,
    }


@pytest.mark.asyncio
async def test_update_task(
    client: TestClient, app: FastAPI, task_controller: TaskController
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

    _id = uuid.uuid4()

    task_update_data = {
        "title": "Supermarket",
        "description": "John Doe is going to the supermarket",
        "completed": False,
        "category": "Groceries",
    }

    updated_task = Task(
        id=_id,
        created_at=datetime(2020, 1, 1),
        **task_update_data,
        user_id=mock_user.id,
    )

    def _mock_update_task():
        task_controller.update_task = AsyncMock(return_value=updated_task)
        return task_controller

    app.dependency_overrides[get_task_controller] = _mock_update_task

    update_task_response = client.patch(f"/tasks/{_id}", json=task_update_data)
    assert update_task_response.status_code == 200
    assert update_task_response.json() == {
        "id": str(_id),
        "created_at": updated_task.created_at.isoformat(),
        "title": updated_task.title,
        "description": updated_task.description,
        "completed": updated_task.completed,
        "category": updated_task.category,
        "user_id": str(mock_user.id),
    }


@pytest.mark.asyncio
async def test_update_task_raise_task_not_found_error(
    task_controller: TaskController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    task_update_data = {
        "title": "Supermarket",
        "description": "John Doe is going to the supermarket",
        "completed": False,
        "category": "Groceries",
    }

    def _mock_update_task():
        task_controller.update_task = AsyncMock(
            side_effect=TaskNotFoundError(task_id=_id)
        )
        return task_controller

    app.dependency_overrides[get_task_controller] = _mock_update_task
    update_task_response = client.patch(f"/tasks/{_id}", json=task_update_data)
    assert update_task_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_task(
    task_controller: TaskController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_delete_task():
        task_controller.delete_task = AsyncMock(return_value=None)
        return task_controller

    app.dependency_overrides[get_task_controller] = _mock_delete_task
    delete_task_response = client.delete(f"/tasks/{_id}")
    assert delete_task_response.status_code == 204


@pytest.mark.asyncio
async def test_delete_task_raise_task_not_found_error(
    task_controller: TaskController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_delete_task():
        task_controller.delete_task = AsyncMock(
            side_effect=TaskNotFoundError(task_id=_id)
        )
        return task_controller

    app.dependency_overrides[get_task_controller] = _mock_delete_task
    delete_task_response = client.delete(f"/tasks/{_id}")
    assert delete_task_response.status_code == 404
