import uuid
from datetime import datetime
from unittest.mock import AsyncMock
import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient
from leveluplife.dependencies import get_item_controller
from leveluplife.controllers.item import ItemController
from leveluplife.models.error import (
    ItemAlreadyExistsError,
    ItemNotFoundError,
    ItemNameNotFoundError,
    ItemInUserNotFoundError,
)
from leveluplife.models.table import Item, User
from leveluplife.models.user import Tribe
from leveluplife.models.view import ItemWithUser


@pytest.mark.asyncio
async def test_create_item(
    item_controller: ItemController, app: FastAPI, client: TestClient
) -> None:
    item_data = {
        "name": "JohnDoe",
        "description": "description test",
        "price_sell": "100",
        "strength": "10",
        "intelligence": "10",
        "agility": "10",
        "wise": "10",
        "psycho": "10",
    }

    mock_item = Item(
        id=uuid.uuid4(),
        created_at=datetime(2020, 1, 1),
        updated_at=datetime(2021, 1, 1),
        deleted_at=None,
        **item_data,
    )

    def _mock_create_item():
        item_controller.create_item = AsyncMock(return_value=mock_item)
        return item_controller

    app.dependency_overrides[get_item_controller] = _mock_create_item

    create_item_response = client.post("/items", json=item_data)
    assert create_item_response.status_code == 201
    actual_response = create_item_response.json()
    assert actual_response == {
        "id": str(mock_item.id),
        "created_at": mock_item.created_at.isoformat(),
        "updated_at": mock_item.updated_at.isoformat(),
        "deleted_at": None,
        "name": mock_item.name,
        "description": mock_item.description,
        "price_sell": mock_item.price_sell,
        "agility": mock_item.agility,
        "intelligence": mock_item.intelligence,
        "psycho": mock_item.psycho,
        "strength": mock_item.strength,
        "wise": mock_item.wise,
    }


@pytest.mark.asyncio
async def test_create_item_raise_item_already_exists_error(
    item_controller: ItemController, app: FastAPI, client: TestClient
):
    item_data = {
        "name": "JohnDoe",
        "description": "description test",
        "price_sell": "100",
        "strength": "10",
        "intelligence": "10",
        "agility": "10",
        "wise": "10",
        "psycho": "10",
    }

    def _mock_create_item():
        item_controller.create_item = AsyncMock(
            side_effect=ItemAlreadyExistsError(_name=item_data["name"])
        )
        return item_controller

    app.dependency_overrides[get_item_controller] = _mock_create_item

    create_item_response = client.post("/items", json=item_data)
    assert create_item_response.status_code == 409
    assert create_item_response.json() == {
        "name": "ItemAlreadyExistsError",
        "message": f"Item with the name {item_data['name']} already exists.",
        "status_code": 409,
    }


@pytest.mark.asyncio
async def test_get_items(
    item_controller: ItemController, client: TestClient, app: FastAPI
) -> None:
    mock_items = [
        Item(
            id=uuid.uuid4(),
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2021, 1, 1),
            deleted_at=None,
            name="JohnDoe",
            description="John Doe is going to the supermarket",
            price_sell=100,
            strength=10,
            intelligence=10,
            agility=10,
            wise=10,
            psycho=10,
        ),
        Item(
            id=uuid.uuid4(),
            created_at=datetime(2020, 1, 1),
            updated_at=datetime(2021, 1, 1),
            deleted_at=None,
            name="JohnDoe2",
            description="John Doe is going to the supermarket",
            price_sell=100,
            strength=10,
            intelligence=10,
            agility=10,
            wise=10,
            psycho=10,
        ),
    ]

    def _mock_get_items():
        item_controller.get_items = AsyncMock(return_value=mock_items)
        return item_controller

    app.dependency_overrides[get_item_controller] = _mock_get_items

    get_item_response = client.get("/items")
    assert get_item_response.status_code == 200
    assert get_item_response.json() == [
        {
            "id": str(item.id),
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat(),
            "deleted_at": None,
            "name": item.name,
            "description": item.description,
            "price_sell": item.price_sell,
            "strength": item.strength,
            "intelligence": item.intelligence,
            "agility": item.agility,
            "wise": item.wise,
            "psycho": item.psycho,
        }
        for item in mock_items
    ]


@pytest.mark.asyncio
async def test_get_item_by_id(
    item_controller: ItemController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_get_item_by_id():
        item_controller.get_item_by_id = AsyncMock(
            return_value=Item(
                id=_id,
                created_at=datetime(2020, 1, 1),
                updated_at=datetime(2021, 1, 1),
                name="Supermarket",
                description="John Doe is going to the supermarket",
                price_sell=100,
                strength=10,
                intelligence=10,
                agility=10,
                wise=10,
                psycho=10,
            ),
        )
        return item_controller

    app.dependency_overrides[get_item_controller] = _mock_get_item_by_id
    get_item_by_id_response = client.get(f"/items/{_id}")
    assert get_item_by_id_response.status_code == 200
    assert get_item_by_id_response.json() == {
        "id": str(_id),
        "created_at": "2020-01-01T00:00:00",
        "updated_at": "2021-01-01T00:00:00",
        "deleted_at": None,
        "name": "Supermarket",
        "description": "John Doe is going to the supermarket",
        "price_sell": 100,
        "strength": 10,
        "intelligence": 10,
        "agility": 10,
        "wise": 10,
        "psycho": 10,
        "users": [],
    }


@pytest.mark.asyncio
async def test_get_item_by_id_raise_item_not_found_error(
    item_controller: ItemController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_get_item_by_id():
        item_controller.get_item_by_id = AsyncMock(
            side_effect=ItemNotFoundError(item_id=_id)
        )
        return item_controller

    app.dependency_overrides[get_item_controller] = _mock_get_item_by_id

    get_item_by_id_response = client.get(f"/items/{_id}")
    assert get_item_by_id_response.status_code == 404
    assert get_item_by_id_response.json() == {
        "message": f"Item with ID {_id} not found",
        "name": "ItemNotFoundError",
        "status_code": 404,
    }


@pytest.mark.asyncio
async def test_get_item_by_name(
    item_controller: ItemController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_get_item_by_name():
        item_controller.get_item_by_name = AsyncMock(
            return_value=Item(
                id=_id,
                created_at=datetime(2020, 1, 1),
                updated_at=datetime(2021, 1, 1),
                name="Supermarket",
                description="John Doe is going to the supermarket",
                price_sell=100,
                strength=10,
                intelligence=10,
                agility=10,
                wise=10,
                psycho=10,
            ),
        )
        return item_controller

    app.dependency_overrides[get_item_controller] = _mock_get_item_by_name
    get_item_by_name_response = client.get("/items/type/name?item_name=Supermarket")
    assert get_item_by_name_response.status_code == 200
    assert get_item_by_name_response.json() == {
        "id": str(_id),
        "created_at": "2020-01-01T00:00:00",
        "updated_at": "2021-01-01T00:00:00",
        "deleted_at": None,
        "name": "Supermarket",
        "description": "John Doe is going to the supermarket",
        "price_sell": 100,
        "strength": 10,
        "intelligence": 10,
        "agility": 10,
        "wise": 10,
        "psycho": 10,
    }


@pytest.mark.asyncio
async def test_get_item_by_name_raise_item_name_not_found_error(
    item_controller: ItemController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_get_item_by_name():
        item_controller.get_item_by_name = AsyncMock(
            side_effect=ItemNameNotFoundError(item_name="Supermarket")
        )
        return item_controller

    app.dependency_overrides[get_item_controller] = _mock_get_item_by_name

    get_item_by_name_response = client.get("/items/type/name?item_name=Supermarket")
    assert get_item_by_name_response.status_code == 404
    assert get_item_by_name_response.json() == {
        "message": "Item with name Supermarket not found",
        "name": "ItemNameNotFoundError",
        "status_code": 404,
    }


@pytest.mark.asyncio
async def test_update_item(
    client: TestClient, app: FastAPI, item_controller: ItemController
) -> None:
    _id = uuid.uuid4()

    item_update_data = {
        "name": "JohnDoe",
        "description": "description test",
        "price_sell": "100",
        "strength": "10",
        "intelligence": "10",
        "agility": "10",
        "wise": "10",
        "psycho": "10",
    }

    updated_item = Item(
        id=_id,
        created_at=datetime(2020, 1, 1),
        updated_at=datetime(2021, 1, 1),
        deleted_at=None,
        **item_update_data,
    )

    def _mock_update_item():
        item_controller.update_item = AsyncMock(return_value=updated_item)
        return item_controller

    app.dependency_overrides[get_item_controller] = _mock_update_item

    update_item_response = client.patch(f"/items/{_id}", json=item_update_data)
    assert update_item_response.status_code == 200
    assert update_item_response.json() == {
        "id": str(_id),
        "created_at": updated_item.created_at.isoformat(),
        "updated_at": updated_item.updated_at.isoformat(),
        "deleted_at": None,
        "name": updated_item.name,
        "description": updated_item.description,
        "price_sell": updated_item.price_sell,
        "strength": updated_item.strength,
        "intelligence": updated_item.intelligence,
        "agility": updated_item.agility,
        "wise": updated_item.wise,
        "psycho": updated_item.psycho,
    }


@pytest.mark.asyncio
async def test_update_item_raise_item_not_found_error(
    item_controller: ItemController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    item_update_data = {
        "name": "JohnDoe",
        "description": "description test",
        "price_sell": "100",
        "strength": "10",
        "intelligence": "10",
        "agility": "10",
        "wise": "10",
        "psycho": "10",
    }

    def _mock_update_item():
        item_controller.update_item = AsyncMock(
            side_effect=ItemNotFoundError(item_id=_id)
        )
        return item_controller

    app.dependency_overrides[get_item_controller] = _mock_update_item
    update_item_response = client.patch(f"/items/{_id}", json=item_update_data)
    assert update_item_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_item(
    item_controller: ItemController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_delete_item():
        item_controller.delete_item = AsyncMock(return_value=None)
        return item_controller

    app.dependency_overrides[get_item_controller] = _mock_delete_item
    delete_item_response = client.delete(f"/items/{_id}")
    assert delete_item_response.status_code == 204


@pytest.mark.asyncio
async def test_delete_item_raise_item_not_found_error(
    item_controller: ItemController, client: TestClient, app: FastAPI
) -> None:
    _id = uuid.uuid4()

    def _mock_delete_item():
        item_controller.delete_item = AsyncMock(
            side_effect=ItemNotFoundError(item_id=_id)
        )
        return item_controller

    app.dependency_overrides[get_item_controller] = _mock_delete_item
    delete_item_response = client.delete(f"/items/{_id}")
    assert delete_item_response.status_code == 404


@pytest.mark.asyncio
async def test_give_item_to_user(
    item_controller: ItemController, app: FastAPI, client: TestClient
) -> None:
    item_id = uuid.uuid4()
    user_id = uuid.uuid4()
    user_item_link_create = {"user_ids": [str(user_id)]}

    def _mock_give_item_to_user():
        item_controller.give_item_to_user = AsyncMock(
            return_value=ItemWithUser(
                id=item_id,
                created_at=datetime(2020, 1, 1),
                updated_at=datetime(2021, 1, 1),
                deleted_at=None,
                name="Supermarket",
                description="John Doe is going to the supermarket",
                price_sell=100,
                strength=10,
                intelligence=10,
                agility=10,
                wise=10,
                psycho=10,
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
                    )
                ],
            )
        )
        return item_controller

    app.dependency_overrides[get_item_controller] = _mock_give_item_to_user

    give_item_response = client.patch(
        f"/items/{item_id}/link_user", json=user_item_link_create
    )

    assert give_item_response.status_code == 200
    assert give_item_response.json() == {
        "id": str(item_id),
        "created_at": "2020-01-01T00:00:00",
        "updated_at": "2021-01-01T00:00:00",
        "deleted_at": None,
        "name": "Supermarket",
        "description": "John Doe is going to the supermarket",
        "price_sell": 100,
        "strength": 10,
        "intelligence": 10,
        "agility": 10,
        "wise": 10,
        "psycho": 10,
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
async def test_remove_item_from_user(
    item_controller: ItemController, app: FastAPI, client: TestClient
) -> None:
    item_id = uuid.uuid4()
    user_id = uuid.uuid4()

    def _mock_remove_item_from_user():
        item_controller.remove_item_from_user = AsyncMock(return_value=None)
        return item_controller

    app.dependency_overrides[get_item_controller] = _mock_remove_item_from_user

    remove_item_response = client.delete(f"/items/{item_id}/unlink_user/{user_id}")
    assert remove_item_response.status_code == 204


@pytest.mark.asyncio
async def test_remove_item_from_user_raise_item_in_user_not_found_error(
    item_controller: ItemController, app: FastAPI, client: TestClient
) -> None:
    item_id = uuid.uuid4()
    user_id = uuid.uuid4()

    def _mock_remove_item_from_user():
        item_controller.remove_item_from_user = AsyncMock(
            side_effect=ItemInUserNotFoundError(item_id=item_id, user_id=user_id)
        )
        return item_controller

    app.dependency_overrides[get_item_controller] = _mock_remove_item_from_user

    remove_item_response = client.delete(f"/items/{item_id}/unlink_user/{user_id}")
    assert remove_item_response.status_code == 404
    assert remove_item_response.json() == {
        "message": f"Item: {item_id} in User: {user_id} not found.",
        "name": "ItemInUserNotFoundError",
        "status_code": 404,
    }
