import uuid
from datetime import datetime
from unittest.mock import AsyncMock
from uuid import UUID
import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from leveluplife.controllers.comment import CommentController
from leveluplife.dependencies import get_comment_controller
from leveluplife.models.error import CommentAlreadyExistsError, CommentNotFoundError
from leveluplife.models.table import Comment, User, Task
from leveluplife.models.user import Tribe


@pytest.mark.asyncio
async def test_create_comment(
    comment_controller: CommentController, app: FastAPI, client: TestClient
) -> None:
    comment_data = {
        "content": "This is a comment",
        "user_id": str(uuid.uuid4()),
        "task_id": str(uuid.uuid4()),
    }

    mock_comment = Comment(
        id=uuid.uuid4(),
        created_at=datetime(2020, 1, 1),
        updated_at=datetime(2021, 1, 1),
        deleted_at=None,
        **comment_data,
    )

    def _mock_create_comment():
        comment_controller.create_comment = AsyncMock(return_value=mock_comment)
        return comment_controller

    app.dependency_overrides[get_comment_controller] = _mock_create_comment

    create_comment_response = client.post("/comments", json=comment_data)
    assert create_comment_response.status_code == 201
    assert create_comment_response.json() == {
        "id": str(mock_comment.id),
        "created_at": mock_comment.created_at.isoformat(),
        "updated_at": mock_comment.updated_at.isoformat(),
        "deleted_at": None,
        "content": mock_comment.content,
        "user_id": str(mock_comment.user_id),
        "task_id": str(mock_comment.task_id),
    }


@pytest.mark.asyncio
async def test_create_comment_raise_comment_already_exists_error(
    comment_controller: CommentController, app: FastAPI, client: TestClient
):
    comment_data = {
        "content": "This is a comment",
        "user_id": str(uuid.uuid4()),
        "task_id": str(uuid.uuid4()),
    }

    def _mock_create_comment():
        comment_controller.create_comment = AsyncMock(
            side_effect=CommentAlreadyExistsError(task_id=UUID(comment_data["task_id"]))
        )
        return comment_controller

    app.dependency_overrides[get_comment_controller] = _mock_create_comment

    create_comment_response = client.post("/comments", json=comment_data)
    assert create_comment_response.status_code == 409
    assert create_comment_response.json() == {
        "name": "CommentAlreadyExistsError",
        "message": f"Comment for the task {comment_data['task_id']} already exists.",
        "status_code": 409,
    }


@pytest.mark.asyncio
async def test_get_comments(
    comment_controller: CommentController, client: TestClient, app: FastAPI
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

    mock_comments = [
        Comment(
            id=uuid.uuid4(),
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2021, 1, 1),
            deleted_at=None,
            task_id=mock_tasks[0].id,
            user_id=mock_user.id,
            content="This is a comment",
        ),
        Comment(
            id=uuid.uuid4(),
            created_at=datetime(2022, 2, 2),
            updated_at=datetime(2021, 1, 1),
            deleted_at=None,
            task_id=mock_tasks[1].id,
            user_id=mock_user.id,
            content="This is a comment",
        ),
    ]

    def _mock_get_comments():
        comment_controller.get_comments = AsyncMock(return_value=mock_comments)
        return comment_controller

    app.dependency_overrides[get_comment_controller] = _mock_get_comments

    get_comment_response = client.get("/comments")
    assert get_comment_response.status_code == 200
    assert get_comment_response.json() == [
        {
            "id": str(comment.id),
            "created_at": comment.created_at.isoformat(),
            "updated_at": comment.updated_at.isoformat(),
            "deleted_at": None,
            "task_id": str(comment.task_id),
            "user_id": str(comment.user_id),
            "content": comment.content,
        }
        for comment in mock_comments
    ]


@pytest.mark.asyncio
async def test_get_comment_by_id(
    comment_controller: CommentController, client: TestClient, app: FastAPI
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

    mock_comment = Comment(
        id=uuid.uuid4(),
        created_at=datetime(2020, 1, 1),
        updated_at=datetime(2021, 1, 1),
        deleted_at=None,
        task_id=mock_task.id,
        user_id=mock_user.id,
        content="This is a comment",
    )

    def _mock_get_comment_by_id():
        comment_controller.get_comment_by_id = AsyncMock(
            return_value=mock_comment,
        )
        return comment_controller

    app.dependency_overrides[get_comment_controller] = _mock_get_comment_by_id
    get_comment_by_id_response = client.get(f"/comments/{mock_comment.id}")
    assert get_comment_by_id_response.status_code == 200
    assert get_comment_by_id_response.json() == {
        "id": str(mock_comment.id),
        "created_at": mock_comment.created_at.isoformat(),
        "updated_at": mock_comment.updated_at.isoformat(),
        "deleted_at": None,
        "task_id": str(mock_comment.task_id),
        "user_id": str(mock_comment.user_id),
        "content": mock_comment.content,
    }


@pytest.mark.asyncio
async def test_get_comment_by_id_raise_comment_not_found_error(
    comment_controller: CommentController, client: TestClient, app: FastAPI
) -> None:
    mock_comment_id = uuid.uuid4()

    def _mock_get_comment_by_id():
        comment_controller.get_comment_by_id = AsyncMock(
            side_effect=CommentNotFoundError(comment_id=mock_comment_id)
        )
        return comment_controller

    app.dependency_overrides[get_comment_controller] = _mock_get_comment_by_id

    get_comment_by_id_response = client.get(f"/comments/{mock_comment_id}")
    assert get_comment_by_id_response.status_code == 404
    assert get_comment_by_id_response.json() == {
        "message": f"Comment with ID {mock_comment_id} not found",
        "name": "CommentNotFoundError",
        "status_code": 404,
    }


@pytest.mark.asyncio
async def test_update_comment(
    comment_controller: CommentController, client: TestClient, app: FastAPI
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

    mock_comment_id = uuid.uuid4()

    comment_update_data = {
        "content": "This is a comment",
    }

    updated_comment = Comment(
        id=mock_comment_id,
        **comment_update_data,
        created_at=datetime(2020, 1, 1),
        updated_at=datetime(2021, 1, 1),
        deleted_at=None,
        task_id=mock_task.id,
        user_id=mock_user.id,
    )

    def _mock_update_comment():
        comment_controller.update_comment = AsyncMock(return_value=updated_comment)
        return comment_controller

    app.dependency_overrides[get_comment_controller] = _mock_update_comment

    update_comment_response = client.patch(
        f"/comments/{mock_comment_id}", json=comment_update_data
    )
    assert update_comment_response.status_code == 200
    assert update_comment_response.json() == {
        "id": str(updated_comment.id),
        "created_at": updated_comment.created_at.isoformat(),
        "updated_at": updated_comment.updated_at.isoformat(),
        "deleted_at": None,
        "task_id": str(updated_comment.task_id),
        "user_id": str(updated_comment.user_id),
        "content": updated_comment.content,
    }


@pytest.mark.asyncio
async def test_update_comment_raise_comment_not_found_error(
    comment_controller: CommentController, client: TestClient, app: FastAPI
) -> None:
    mock_comment_id = uuid.uuid4()

    comment_update_data = {
        "content": "This is a comment",
    }

    def _mock_update_comment():
        comment_controller.update_comment = AsyncMock(
            side_effect=CommentNotFoundError(comment_id=mock_comment_id)
        )
        return comment_controller

    app.dependency_overrides[get_comment_controller] = _mock_update_comment

    update_comment_response = client.patch(
        f"/comments/{mock_comment_id}", json=comment_update_data
    )
    assert update_comment_response.status_code == 404
    assert update_comment_response.json() == {
        "message": f"Comment with ID {mock_comment_id} not found",
        "name": "CommentNotFoundError",
        "status_code": 404,
    }


@pytest.mark.asyncio
async def test_delete_comment(
    comment_controller: CommentController, client: TestClient, app: FastAPI
) -> None:
    mock_comment_id = uuid.uuid4()

    def _mock_delete_comment():
        comment_controller.delete_comment = AsyncMock(return_value=None)
        return comment_controller

    app.dependency_overrides[get_comment_controller] = _mock_delete_comment
    delete_comment_response = client.delete(f"/comments/{mock_comment_id}")
    assert delete_comment_response.status_code == 204


@pytest.mark.asyncio
async def test_delete_comment_raise_comment_not_found_error(
    comment_controller: CommentController, client: TestClient, app: FastAPI
) -> None:
    mock_comment_id = uuid.uuid4()

    def _mock_delete_comment():
        comment_controller.delete_comment = AsyncMock(
            side_effect=CommentNotFoundError(comment_id=mock_comment_id)
        )
        return comment_controller

    app.dependency_overrides[get_comment_controller] = _mock_delete_comment

    delete_comment_response = client.delete(f"/comments/{mock_comment_id}")
    assert delete_comment_response.status_code == 404
    assert delete_comment_response.json() == {
        "message": f"Comment with ID {mock_comment_id} not found",
        "name": "CommentNotFoundError",
        "status_code": 404,
    }
