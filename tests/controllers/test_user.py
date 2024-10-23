import random

import pytest
from faker import Faker
from sqlmodel import Session, select

from leveluplife.auth.hash import verify_password
from leveluplife.controllers.item import ItemController
from leveluplife.controllers.user import UserController
from leveluplife.models.error import (
    UserEmailAlreadyExistsError,
    UserEmailNotFoundError,
    UserNotFoundError,
    UserUsernameAlreadyExistsError,
    UserUsernameNotFoundError,
    ItemLinkToUserNotFoundError,
)
from leveluplife.models.item import ItemCreate
from leveluplife.models.relationship import UserItemLinkCreate
from leveluplife.models.table import User
from leveluplife.models.user import Tribe, UserCreate, UserUpdate
from leveluplife.models.view import UserView

# Dictionary of expected stats for each tribe
expected_stats = {
    "Nosferati": {
        "intelligence": 8,
        "strength": 2,
        "agility": 2,
        "wise": 1,
        "psycho": 10,
    },
    "Valhars": {
        "intelligence": 1,
        "strength": 10,
        "agility": 6,
        "wise": 6,
        "psycho": 2,
    },
    "Saharans": {
        "intelligence": 9,
        "strength": 2,
        "agility": 3,
        "wise": 10,
        "psycho": 1,
    },
    "Glimmerkins": {
        "intelligence": 10,
        "strength": 2,
        "agility": 2,
        "wise": 7,
        "psycho": 4,
    },
    "Neutrals": {
        "intelligence": 5,
        "strength": 5,
        "agility": 5,
        "wise": 5,
        "psycho": 5,
    },
}


@pytest.mark.asyncio
async def test_create_user_nosferati(
    user_controller: UserController, session: Session, faker: Faker
) -> None:
    # Prepare
    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=Tribe("Nosferati"),
    )
    # Act
    result = await user_controller.create_user(user_create)

    user = session.exec(select(User).where(User.id == result.id)).one()

    # Assert
    assert result.username == user_create.username == user.username
    assert result.email == user_create.email == user.email
    assert verify_password(user_create.password, user.password)
    assert result.tribe == user_create.tribe == user.tribe
    assert result.intelligence == expected_stats["Nosferati"]["intelligence"]
    assert result.strength == expected_stats["Nosferati"]["strength"]
    assert result.agility == expected_stats["Nosferati"]["agility"]
    assert result.wise == expected_stats["Nosferati"]["wise"]
    assert result.psycho == expected_stats["Nosferati"]["psycho"]


@pytest.mark.asyncio
async def test_create_user_valhars(
    user_controller: UserController, session: Session, faker: Faker
) -> None:
    # Prepare
    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=Tribe("Valhars"),
    )
    # Act
    result = await user_controller.create_user(user_create)

    user = session.exec(select(User).where(User.id == result.id)).one()

    # Assert
    assert result.username == user_create.username == user.username
    assert result.email == user_create.email == user.email
    assert verify_password(user_create.password, user.password)
    assert result.tribe == user_create.tribe == user.tribe
    assert result.intelligence == expected_stats["Valhars"]["intelligence"]
    assert result.strength == expected_stats["Valhars"]["strength"]
    assert result.agility == expected_stats["Valhars"]["agility"]
    assert result.wise == expected_stats["Valhars"]["wise"]
    assert result.psycho == expected_stats["Valhars"]["psycho"]


@pytest.mark.asyncio
async def test_create_user_saharans(
    user_controller: UserController, session: Session, faker: Faker
) -> None:
    # Prepare
    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=Tribe("Saharans"),
    )
    # Act
    result = await user_controller.create_user(user_create)

    user = session.exec(select(User).where(User.id == result.id)).one()

    # Assert
    assert result.username == user_create.username == user.username
    assert result.email == user_create.email == user.email
    assert verify_password(user_create.password, user.password)
    assert result.tribe == user_create.tribe == user.tribe
    assert result.intelligence == expected_stats["Saharans"]["intelligence"]
    assert result.strength == expected_stats["Saharans"]["strength"]
    assert result.agility == expected_stats["Saharans"]["agility"]
    assert result.wise == expected_stats["Saharans"]["wise"]
    assert result.psycho == expected_stats["Saharans"]["psycho"]


@pytest.mark.asyncio
async def test_create_user_glimmerkins(
    user_controller: UserController, session: Session, faker: Faker
) -> None:
    # Prepare
    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=Tribe("Glimmerkins"),
    )
    # Act
    result = await user_controller.create_user(user_create)

    user = session.exec(select(User).where(User.id == result.id)).one()

    # Assert
    assert result.username == user_create.username == user.username
    assert result.email == user_create.email == user.email
    assert verify_password(user_create.password, user.password)
    assert result.tribe == user_create.tribe == user.tribe
    assert result.intelligence == expected_stats["Glimmerkins"]["intelligence"]
    assert result.strength == expected_stats["Glimmerkins"]["strength"]
    assert result.agility == expected_stats["Glimmerkins"]["agility"]
    assert result.wise == expected_stats["Glimmerkins"]["wise"]
    assert result.psycho == expected_stats["Glimmerkins"]["psycho"]


@pytest.mark.asyncio
async def test_create_user_neutrals(
    user_controller: UserController, session: Session, faker: Faker
) -> None:
    # Prepare
    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=Tribe("Neutrals"),
    )
    # Act
    result = await user_controller.create_user(user_create)

    user = session.exec(select(User).where(User.id == result.id)).one()

    # Assert
    assert result.username == user_create.username == user.username
    assert result.email == user_create.email == user.email
    assert verify_password(user_create.password, user.password)
    assert result.tribe == user_create.tribe == user.tribe
    assert result.intelligence == expected_stats["Neutrals"]["intelligence"]
    assert result.strength == expected_stats["Neutrals"]["strength"]
    assert result.agility == expected_stats["Neutrals"]["agility"]
    assert result.wise == expected_stats["Neutrals"]["wise"]
    assert result.psycho == expected_stats["Neutrals"]["psycho"]


@pytest.mark.asyncio
async def test_create_user_email_already_exists_error(
    user_controller: UserController, faker: Faker
) -> None:
    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )

    # Act
    await user_controller.create_user(user_create)

    # Assert
    with pytest.raises(UserEmailAlreadyExistsError):
        await user_controller.create_user(user_create)


@pytest.mark.asyncio
async def test_create_user_username_already_exists_error(
    user_controller: UserController, faker: Faker
) -> None:
    existing_username = "existing_user"
    existing_user_create = UserCreate(
        username=existing_username,
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )

    await user_controller.create_user(existing_user_create)

    user_create = UserCreate(
        username=existing_username,
        email=faker.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )

    with pytest.raises(UserUsernameAlreadyExistsError):
        await user_controller.create_user(user_create)


@pytest.mark.asyncio
async def test_get_users(user_controller: UserController, faker: Faker) -> None:
    number_users = 5
    created_users = []
    for _ in range(number_users):
        user_create = UserCreate(
            username=faker.unique.user_name()[:18],
            email=faker.unique.email(),
            password=faker.password(),
            tribe=random.choice(list(Tribe)),
        )
        created_user = await user_controller.create_user(user_create)
        created_users.append(created_user)

    all_users = await user_controller.get_users(offset=0, limit=20)
    created_users.sort(key=lambda u: u.username)
    assert len(all_users) == number_users

    for i, created_user in enumerate(created_users):
        assert all_users[i].username == created_user.username
        assert all_users[i].email == created_user.email
        assert all_users[i].tribe == created_user.tribe
        assert all_users[i].intelligence == created_user.intelligence
        assert all_users[i].strength == created_user.strength
        assert all_users[i].agility == created_user.agility
        assert all_users[i].wise == created_user.wise
        assert all_users[i].psycho == created_user.psycho


@pytest.mark.asyncio
async def test_get_user_by_id(user_controller: UserController, faker: Faker) -> None:
    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )

    created_user = await user_controller.create_user(user_create)

    retrieved_user = await user_controller.get_user_by_id(created_user.id)

    assert retrieved_user.username == user_create.username
    assert retrieved_user.email == user_create.email
    assert retrieved_user.tribe == user_create.tribe


@pytest.mark.asyncio
async def test_get_user_by_id_raise_user_not_found_error(
    user_controller: UserController, faker: Faker
) -> None:
    non_existent_user_id = faker.uuid4()
    with pytest.raises(UserNotFoundError):
        await user_controller.get_user_by_id(non_existent_user_id)


@pytest.mark.asyncio
async def test_get_user_by_username(
    user_controller: UserController, faker: Faker
) -> None:
    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )

    created_user = await user_controller.create_user(user_create)

    retrieved_user = await user_controller.get_user_by_username(created_user.username)

    assert retrieved_user.username == user_create.username
    assert retrieved_user.email == user_create.email
    assert retrieved_user.tribe == user_create.tribe


@pytest.mark.asyncio
async def test_get_user_by_username_raise_user_username_not_found_error(
    user_controller: UserController, faker: Faker
) -> None:
    non_existent_user_username = faker.unique.user_name()
    with pytest.raises(UserUsernameNotFoundError):
        await user_controller.get_user_by_username(non_existent_user_username)


@pytest.mark.asyncio
async def test_get_user_by_email(user_controller: UserController, faker: Faker) -> None:
    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )

    created_user = await user_controller.create_user(user_create)

    retrieved_user = await user_controller.get_user_by_email(created_user.email)

    assert retrieved_user.username == user_create.username
    assert retrieved_user.email == user_create.email
    assert retrieved_user.tribe == user_create.tribe


@pytest.mark.asyncio
async def test_get_user_by_email_raise_user_email_not_found_error(
    user_controller: UserController, faker: Faker
) -> None:
    non_existent_user_email = faker.unique.email()
    with pytest.raises(UserEmailNotFoundError):
        await user_controller.get_user_by_email(non_existent_user_email)


@pytest.mark.asyncio
async def test_get_users_by_tribe(
    user_controller: UserController, faker: Faker
) -> None:
    number_users = 5
    created_users = []
    tribes = list(Tribe)

    # Create users with random tribes
    for _ in range(number_users):
        user_create = UserCreate(
            username=faker.unique.user_name()[:18],
            email=faker.unique.email(),
            password=faker.password(),
            tribe=random.choice(tribes),
        )
        created_user = await user_controller.create_user(user_create)
        created_users.append(created_user)

    # Test fetching users by tribe
    for tribe in tribes:
        tribe_users: list[UserView] = await user_controller.get_users_by_tribe(
            tribe.value, offset=0 * 20, limit=20
        )
        filtered_users = [user for user in created_users if user.tribe == tribe]

        assert len(tribe_users) == len(filtered_users)

        for tribe_user in tribe_users:
            assert tribe_user.tribe == tribe


@pytest.mark.asyncio
async def test_update_user(user_controller: UserController, faker: Faker) -> None:
    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )
    new_user = await user_controller.create_user(user_create)

    user_update = UserUpdate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        tribe=random.choice(list(Tribe)),
    )

    updated_user = await user_controller.update_user(new_user.id, user_update)

    assert updated_user.id == new_user.id
    assert updated_user.username == user_update.username
    assert updated_user.email == user_update.email
    assert updated_user.tribe == user_update.tribe


@pytest.mark.asyncio
async def test_update_user_raise_user_not_found_error(
    user_controller: UserController, faker: Faker
) -> None:
    user_update = UserUpdate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        tribe=random.choice(list(Tribe)),
    )

    nonexistent_user_id = faker.uuid4()

    with pytest.raises(UserNotFoundError):
        await user_controller.update_user(nonexistent_user_id, user_update)


@pytest.mark.asyncio
async def test_delete_user(user_controller: UserController, faker: Faker) -> None:
    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )
    new_user = await user_controller.create_user(user_create)

    await user_controller.delete_user(new_user.id)

    with pytest.raises(UserNotFoundError):
        await user_controller.delete_user(new_user.id)


@pytest.mark.asyncio
async def test_delete_user_raise_user_not_found_error(
    user_controller: UserController, faker: Faker
) -> None:
    nonexistent_user_id = faker.uuid4()

    with pytest.raises(UserNotFoundError):
        await user_controller.delete_user(nonexistent_user_id)


@pytest.mark.asyncio
async def test_update_user_password(
    user_controller: UserController, faker: Faker, session: Session
) -> None:
    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )
    new_user = await user_controller.create_user(user_create)

    new_password = faker.password()
    await user_controller.update_user_password(new_user.id, new_password)

    updated_user = session.exec(select(User).where(User.id == new_user.id)).one()
    assert updated_user.password == new_password
    assert updated_user.id == new_user.id
    assert updated_user.username == new_user.username
    assert updated_user.email == new_user.email
    assert updated_user.tribe == new_user.tribe
    assert updated_user.password == new_password


@pytest.mark.asyncio
async def test_update_user_password_raise_user_not_found_error(
    user_controller: UserController, faker: Faker
) -> None:
    nonexistent_user_id = faker.uuid4()
    new_password = faker.password()

    with pytest.raises(UserNotFoundError):
        await user_controller.update_user_password(nonexistent_user_id, new_password)


@pytest.mark.asyncio
async def test_equip_item_to_user(
    user_controller: UserController, item_controller: ItemController, faker: Faker
):
    # Create a user through UserController
    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )
    user = await user_controller.create_user(user_create)

    # Create an item through ItemController
    item_create = ItemCreate(
        name=faker.word(),
        description=faker.sentence(),
        price_sell=random.randint(0, 100),
        strength=random.randint(0, 100),
        intelligence=random.randint(0, 100),
        agility=random.randint(0, 100),
        wise=random.randint(0, 100),
        psycho=random.randint(0, 100),
    )
    item = await item_controller.create_item(item_create)

    # Link the item to the user
    user_item_link_create = UserItemLinkCreate(user_ids=[user.id])
    await item_controller.give_item_to_user(item.id, user_item_link_create)

    # Equip the item to the user
    updated_user = await user_controller.equip_item_to_user(user.id, item.id, True)

    # Assert the updated user contains the equipped item
    assert isinstance(updated_user, UserView)
    assert any(
        item_view.id == item.id and item_view.equipped
        for item_view in updated_user.items
    )


@pytest.mark.asyncio
async def test_equip_item_to_user_user_not_found(
    user_controller: UserController, faker: Faker
):
    non_existent_user_id = faker.uuid4()
    non_existent_item_id = faker.uuid4()

    with pytest.raises(UserNotFoundError):
        await user_controller.equip_item_to_user(
            non_existent_user_id, non_existent_item_id, True
        )


@pytest.mark.asyncio
async def test_equip_item_to_user_item_link_not_found(
    user_controller: UserController, faker: Faker
):
    # Create a user through UserController
    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )
    user = await user_controller.create_user(user_create)

    non_existent_item_id = faker.uuid4()

    with pytest.raises(ItemLinkToUserNotFoundError):
        await user_controller.equip_item_to_user(user.id, non_existent_item_id, True)
