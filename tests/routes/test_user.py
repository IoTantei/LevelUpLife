import uuid
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from leveluplife.controllers.user import UserController
from leveluplife.dependencies import get_user_controller
from leveluplife.models.error import (
    UserEmailAlreadyExistsError,
    UserEmailNotFoundError,
    UserNotFoundError,
    UserUsernameAlreadyExistsError,
    UserUsernameNotFoundError,
)
from leveluplife.models.table import User
from leveluplife.models.user import Tribe
from leveluplife.models.view import UserView, ItemUserView


@pytest.mark.asyncio
async def test_create_user(
    user_controller: UserController, app: FastAPI, client: TestClient
) -> None:
    user_data = {
        "username": "JohnDoe",
        "email": "john.doe@test.com",
        "password": "johndoepassword",
        "tribe": "Nosferati",
    }

    mock_user = User(
        id=uuid.uuid4(),
        created_at=datetime(2020, 1, 1),
        tribe=Tribe(user_data["tribe"]),
        **{k: v for k, v in user_data.items() if k != "tribe"},
    )

    def _mock_create_user():
        user_controller.create_user = AsyncMock(return_value=mock_user)
        return user_controller

    app.dependency_overrides[get_user_controller] = _mock_create_user

    create_user_response = client.post("/users", json=user_data)
    assert create_user_response.status_code == 201
    actual_response = create_user_response.json()
    assert actual_response == {
        "id": str(mock_user.id),
        "created_at": mock_user.created_at.isoformat(),
        "items": [],
        "username": mock_user.username,
        "email": mock_user.email,
        "tribe": mock_user.tribe,
        "agility": mock_user.agility,
        "background_image": mock_user.background_image,
        "biography": mock_user.biography,
        "experience": mock_user.experience,
        "intelligence": mock_user.intelligence,
        "profile_picture": mock_user.profile_picture,
        "psycho": mock_user.psycho,
        "strength": mock_user.strength,
        "wise": mock_user.wise,
        "tasks": [],
        "ratings": [],
        "comments": [],
        "reactions": [],
        "quests": [],
    }


@pytest.mark.asyncio
async def test_create_user_raise_user_email_already_exists_error(
    user_controller: UserController, client: TestClient, app: FastAPI
) -> None:
    user_data = {
        "username": "JohnDoe",
        "email": "john.doe@test.com",
        "password": "johndoepassword",
        "tribe": "Nosferati",
    }

    def _mock_create_user():
        user_controller.create_user = AsyncMock(
            side_effect=UserEmailAlreadyExistsError(email=user_data["email"])
        )
        return user_controller

    app.dependency_overrides[get_user_controller] = _mock_create_user

    create_user_response = client.post("/users", json=user_data)
    assert create_user_response.status_code == 409
    assert create_user_response.json() == {
        "name": "UserEmailAlreadyExistsError",
        "message": f"User with the email {user_data['email']} already exists.",
        "status_code": 409,
    }


@pytest.mark.asyncio
async def test_create_user_raise_user_username_already_exists_error(
    user_controller: UserController, client: TestClient, app: FastAPI
) -> None:
    user_data = {
        "username": "JohnDoe",
        "email": "john.doe@test.com",
        "password": "johndoepassword",
        "tribe": "Nosferati",
    }

    def _mock_create_user():
        user_controller.create_user = AsyncMock(
            side_effect=UserUsernameAlreadyExistsError(username=user_data["username"])
        )
        return user_controller

    app.dependency_overrides[get_user_controller] = _mock_create_user

    create_user_response = client.post("/users", json=user_data)
    assert create_user_response.status_code == 409
    assert create_user_response.json() == {
        "name": "UserUsernameAlreadyExistsError",
        "message": f"User with the username {user_data['username']} already exists.",
        "status_code": 409,
    }


@pytest.mark.asyncio
async def test_get_users(
    user_controller: UserController, client: TestClient, app: FastAPI
) -> None:
    mock_users = [
        User(
            id=uuid.uuid4(),
            created_at=datetime(2020, 1, 1),
            tribe=Tribe("Nosferati"),
            username="JohnDoe",
            email="john.doe@test.com",
            password="johndoepassword",
        ),
        User(
            id=uuid.uuid4(),
            created_at=datetime(2022, 2, 2),
            tribe=Tribe("Saharans"),
            username="JaneDoe",
            email="jane.doe@test.com",
            password="janedoepassword",
        ),
    ]

    def _mock_get_users():
        user_controller.get_users = AsyncMock(return_value=mock_users)
        return user_controller

    app.dependency_overrides[get_user_controller] = _mock_get_users

    get_user_response = client.get("/users")
    assert get_user_response.status_code == 200
    assert get_user_response.json() == [
        {
            "id": str(user.id),
            "created_at": user.created_at.isoformat(),
            "items": [],
            "tribe": user.tribe,
            "username": user.username,
            "email": user.email,
            "experience": user.experience,
            "biography": user.biography,
            "background_image": user.background_image,
            "profile_picture": user.profile_picture,
            "agility": user.agility,
            "intelligence": user.intelligence,
            "psycho": user.psycho,
            "strength": user.strength,
            "wise": user.wise,
            "tasks": [],
            "ratings": [],
            "comments": [],
            "reactions": [],
            "quests": [],
        }
        for user in mock_users
    ]


@pytest.mark.asyncio
async def test_get_user_by_id(
    user_controller: UserController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_get_user_by_id():
        user_controller.get_user_by_id = AsyncMock(
            return_value=User(
                id=_id,
                created_at=datetime(2020, 1, 1),
                tribe=Tribe("Neutrals"),
                username="JohnDoe",
                email="john.doe@test.com",
                password="janedoepassword",
            ),
        )
        return user_controller

    app.dependency_overrides[get_user_controller] = _mock_get_user_by_id
    get_user_by_id_response = client.get(f"/users/{_id}")
    assert get_user_by_id_response.status_code == 200
    assert get_user_by_id_response.json() == {
        "id": str(_id),
        "created_at": "2020-01-01T00:00:00",
        "items": [],
        "tribe": "Neutrals",
        "username": "JohnDoe",
        "email": "john.doe@test.com",
        "experience": 0,
        "biography": None,
        "background_image": None,
        "profile_picture": None,
        "agility": 0,
        "intelligence": 0,
        "psycho": 0,
        "strength": 0,
        "wise": 0,
        "tasks": [],
        "ratings": [],
        "comments": [],
        "reactions": [],
        "quests": [],
    }


@pytest.mark.asyncio
async def test_get_user_by_id_raise_user_not_found_error(
    user_controller: UserController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_get_user_by_id():
        user_controller.get_user_by_id = AsyncMock(
            side_effect=UserNotFoundError(user_id=_id)
        )
        return user_controller

    app.dependency_overrides[get_user_controller] = _mock_get_user_by_id

    get_user_by_id_response = client.get(f"/users/{_id}")
    assert get_user_by_id_response.status_code == 404
    assert get_user_by_id_response.json() == {
        "message": f"User with ID {_id} not found",
        "name": "UserNotFoundError",
        "status_code": 404,
    }


@pytest.mark.asyncio
async def test_get_user_by_username(
    user_controller: UserController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_get_user_by_username():
        user_controller.get_user_by_username = AsyncMock(
            return_value=User(
                id=_id,
                created_at=datetime(2020, 1, 1),
                tribe=Tribe("Neutrals"),
                username="JohnDoe",
                email="john.doe@test.com",
                password="janedoepassword",
            ),
        )
        return user_controller

    app.dependency_overrides[get_user_controller] = _mock_get_user_by_username
    get_user_by_username_response = client.get(
        "/users/type/username?user_username=JohnDoe"
    )
    assert get_user_by_username_response.status_code == 200
    assert get_user_by_username_response.json() == {
        "id": str(_id),
        "created_at": "2020-01-01T00:00:00",
        "items": [],
        "tribe": "Neutrals",
        "username": "JohnDoe",
        "email": "john.doe@test.com",
        "experience": 0,
        "biography": None,
        "background_image": None,
        "profile_picture": None,
        "agility": 0,
        "intelligence": 0,
        "psycho": 0,
        "strength": 0,
        "wise": 0,
        "tasks": [],
        "ratings": [],
        "comments": [],
        "reactions": [],
        "quests": [],
    }


@pytest.mark.asyncio
async def test_get_user_by_username_raise_user_username_not_found_error(
    user_controller: UserController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_get_user_by_username():
        user_controller.get_user_by_username = AsyncMock(
            side_effect=UserUsernameNotFoundError(user_username="JohnDoe")
        )
        return user_controller

    app.dependency_overrides[get_user_controller] = _mock_get_user_by_username

    get_user_by_username_response = client.get(
        "/users/type/username?user_username=JohnDoe"
    )
    assert get_user_by_username_response.status_code == 404
    assert get_user_by_username_response.json() == {
        "message": "User with username JohnDoe not found",
        "name": "UserUsernameNotFoundError",
        "status_code": 404,
    }


@pytest.mark.asyncio
async def test_get_user_by_email(
    user_controller: UserController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_get_user_by_email():
        user_controller.get_user_by_email = AsyncMock(
            return_value=User(
                id=_id,
                created_at=datetime(2020, 1, 1),
                tribe=Tribe("Neutrals"),
                username="JohnDoe",
                email="john.doe@test.com",
                password="janedoepassword",
            ),
        )
        return user_controller

    app.dependency_overrides[get_user_controller] = _mock_get_user_by_email
    get_user_by_email_response = client.get(
        "/users/type/email?user_email=john.doe@test.com"
    )
    assert get_user_by_email_response.status_code == 200
    assert get_user_by_email_response.json() == {
        "id": str(_id),
        "created_at": "2020-01-01T00:00:00",
        "items": [],
        "tribe": "Neutrals",
        "username": "JohnDoe",
        "email": "john.doe@test.com",
        "experience": 0,
        "biography": None,
        "background_image": None,
        "profile_picture": None,
        "agility": 0,
        "intelligence": 0,
        "psycho": 0,
        "strength": 0,
        "wise": 0,
        "tasks": [],
        "ratings": [],
        "comments": [],
        "reactions": [],
        "quests": [],
    }


@pytest.mark.asyncio
async def test_get_user_by_email_raise_user_email_not_found_error(
    user_controller: UserController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_get_user_by_email():
        user_controller.get_user_by_email = AsyncMock(
            side_effect=UserEmailNotFoundError(user_email="john.doe@test.com")
        )
        return user_controller

    app.dependency_overrides[get_user_controller] = _mock_get_user_by_email

    get_user_by_email_response = client.get(
        "/users/type/email?user_email=john.doe@test.com"
    )
    assert get_user_by_email_response.status_code == 404
    assert get_user_by_email_response.json() == {
        "message": "User with email john.doe@test.com not found",
        "name": "UserEmailNotFoundError",
        "status_code": 404,
    }


@pytest.mark.asyncio
async def test_get_users_by_tribe(
    client: TestClient, user_controller: UserController, app: FastAPI
) -> None:
    mock_users = [
        User(
            id=uuid.uuid4(),
            created_at=datetime(2020, 1, 1),
            tribe=Tribe.NOSFERATI,
            username="JohnDoe",
            email="john.doe@test.com",
            password="johndoepassword",
        ),
        User(
            id=uuid.uuid4(),
            created_at=datetime(2022, 2, 2),
            tribe=Tribe.NOSFERATI,
            username="JaneDoe",
            email="jane.doe@test.com",
            password="janedoepassword",
        ),
        User(
            id=uuid.uuid4(),
            created_at=datetime(2021, 3, 3),
            tribe=Tribe.SAHARANS,
            username="JimDoe",
            email="jim.doe@test.com",
            password="jimdoepassword",
        ),
    ]

    def _mock_get_users_by_tribe():
        user_controller.get_users_by_tribe = AsyncMock(
            return_value=[user for user in mock_users if user.tribe == Tribe.NOSFERATI]
        )
        return user_controller

    app.dependency_overrides[get_user_controller] = _mock_get_users_by_tribe

    response = client.get("/users/type/tribe?user_tribe=Nosferati")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(user.id),
            "created_at": user.created_at.isoformat(),
            "items": [],
            "tribe": user.tribe,
            "username": user.username,
            "email": user.email,
            "experience": user.experience,
            "biography": user.biography,
            "background_image": user.background_image,
            "profile_picture": user.profile_picture,
            "agility": user.agility,
            "intelligence": user.intelligence,
            "psycho": user.psycho,
            "strength": user.strength,
            "wise": user.wise,
            "tasks": [],
            "ratings": [],
            "comments": [],
            "reactions": [],
            "quests": [],
        }
        for user in mock_users
        if user.tribe == Tribe.NOSFERATI
    ]


@pytest.mark.asyncio
async def test_update_user(
    client: TestClient, app: FastAPI, user_controller: UserController
) -> None:
    _id = uuid.uuid4()

    user_update_data = {
        "tribe": "Neutrals",
        "username": "JohnDoe",
        "email": "john.doe@test.com",
    }

    updated_user = User(
        id=_id,
        created_at=datetime(2020, 1, 1),
        tribe=Tribe(user_update_data["tribe"]),
        **{k: v for k, v in user_update_data.items() if k != "tribe"},
    )

    def _mock_update_user():
        user_controller.update_user = AsyncMock(return_value=updated_user)
        return user_controller

    app.dependency_overrides[get_user_controller] = _mock_update_user

    update_user_response = client.patch(f"/users/{_id}", json=user_update_data)
    assert update_user_response.status_code == 200
    assert update_user_response.json() == {
        "id": str(_id),
        "created_at": updated_user.created_at.isoformat(),
        "items": [],
        "tribe": updated_user.tribe,
        "username": updated_user.username,
        "email": updated_user.email,
        "experience": updated_user.experience,
        "biography": updated_user.biography,
        "background_image": updated_user.background_image,
        "profile_picture": updated_user.profile_picture,
        "agility": updated_user.agility,
        "intelligence": updated_user.intelligence,
        "psycho": updated_user.psycho,
        "strength": updated_user.strength,
        "wise": updated_user.wise,
        "tasks": [],
        "ratings": [],
        "comments": [],
        "reactions": [],
        "quests": [],
    }


@pytest.mark.asyncio
async def test_update_user_raise_user_not_found_error(
    user_controller: UserController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    user_update_data = {
        "tribe": "Neutrals",
        "username": "JohnDoe",
        "email": "john.doe@test.com",
    }

    def _mock_update_user():
        user_controller.update_user = AsyncMock(
            side_effect=UserNotFoundError(user_id=_id)
        )
        return user_controller

    app.dependency_overrides[get_user_controller] = _mock_update_user
    update_user_response = client.patch(f"/users/{_id}", json=user_update_data)
    assert update_user_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user(
    user_controller: UserController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_delete_user():
        user_controller.delete_user = AsyncMock(return_value=None)
        return user_controller

    app.dependency_overrides[get_user_controller] = _mock_delete_user
    delete_user_response = client.delete(f"/users/{_id}")
    assert delete_user_response.status_code == 204


@pytest.mark.asyncio
async def test_delete_user_raise_user_not_found_error(
    user_controller: UserController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_delete_user():
        user_controller.delete_user = AsyncMock(
            side_effect=UserNotFoundError(user_id=_id)
        )
        return user_controller

    app.dependency_overrides[get_user_controller] = _mock_delete_user
    delete_user_response = client.delete(f"/users/{_id}")
    assert delete_user_response.status_code == 404


@pytest.mark.asyncio
async def test_update_user_password(
    user_controller: UserController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    password_date = {"password": "johndoepassword"}

    updated_user = User(
        id=_id,
        created_at=datetime(2020, 1, 1),
        username="JohnDoe",
        email="john.doe@test.com",
        tribe=Tribe("Neutrals"),
        password="johndoepassword",
    )

    def _mock_update_user_password():
        user_controller.update_user_password = AsyncMock(return_value=updated_user)
        return user_controller

    app.dependency_overrides[get_user_controller] = _mock_update_user_password
    update_user_password_response = client.patch(
        f"/users/{_id}/password", json=password_date
    )
    assert update_user_password_response.status_code == 200
    assert update_user_password_response.json() == {
        "id": str(_id),
        "created_at": updated_user.created_at.isoformat(),
        "items": [],
        "tribe": updated_user.tribe,
        "username": updated_user.username,
        "email": updated_user.email,
        "agility": updated_user.agility,
        "intelligence": updated_user.intelligence,
        "psycho": updated_user.psycho,
        "strength": updated_user.strength,
        "wise": updated_user.wise,
        "biography": updated_user.biography,
        "background_image": updated_user.background_image,
        "profile_picture": updated_user.profile_picture,
        "experience": updated_user.experience,
        "tasks": [],
        "ratings": [],
        "comments": [],
        "reactions": [],
        "quests": [],
    }


@pytest.mark.asyncio
async def test_equip_item_to_user(
    user_controller: UserController, client: TestClient, app: FastAPI
) -> None:
    user_id = uuid.uuid4()
    item_id = uuid.uuid4()

    mock_user = UserView(
        id=user_id,
        created_at=datetime(2020, 1, 1),
        username="JohnDoe",
        email="john.doe@test.com",
        tribe=Tribe("Neutrals"),
        biography="Biography",
        profile_picture="Profile picture",
        background_image="Background image",
        strength=0,
        intelligence=0,
        agility=0,
        wise=0,
        psycho=0,
        experience=0,
        items=[],
        tasks=[],
    )

    mock_item = ItemUserView(
        id=item_id,
        created_at=datetime(2020, 1, 1),
        updated_at=datetime(2021, 1, 1),
        deleted_at=None,
        name="Item",
        description="Item description",
        price_sell=0,
        strength=0,
        intelligence=0,
        agility=0,
        wise=0,
        psycho=0,
        equipped=True,
    )

    mock_user.items.append(mock_item)

    def _mock_equip_item_to_user():
        user_controller.equip_item_to_user = AsyncMock(return_value=mock_user)
        return user_controller

    app.dependency_overrides[get_user_controller] = _mock_equip_item_to_user

    equip_item_response = client.post(
        f"/users/{user_id}/items/{item_id}/equip", params={"equipped": True}
    )
    assert equip_item_response.status_code == 200
    actual_response = equip_item_response.json()
    assert actual_response == {
        "id": str(mock_user.id),
        "created_at": mock_user.created_at.isoformat(),
        "items": [
            {
                "id": str(item_id),
                "created_at": mock_item.created_at.isoformat(),
                "updated_at": mock_item.updated_at.isoformat(),
                "deleted_at": None,
                "equipped": True,
                "name": mock_item.name,
                "description": mock_item.description,
                "price_sell": mock_item.price_sell,
                "strength": mock_item.strength,
                "intelligence": mock_item.intelligence,
                "agility": mock_item.agility,
                "wise": mock_item.wise,
                "psycho": mock_item.psycho,
            }
        ],
        "username": mock_user.username,
        "email": mock_user.email,
        "tribe": mock_user.tribe,
        "agility": mock_user.agility,
        "background_image": mock_user.background_image,
        "biography": mock_user.biography,
        "experience": mock_user.experience,
        "intelligence": mock_user.intelligence,
        "profile_picture": mock_user.profile_picture,
        "psycho": mock_user.psycho,
        "strength": mock_user.strength,
        "wise": mock_user.wise,
        "tasks": [],
        "ratings": [],
        "comments": [],
        "reactions": [],
        "quests": [],
    }
