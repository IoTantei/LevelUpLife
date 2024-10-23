import pytest
from faker import Faker
from sqlmodel import select, Session
import random
from leveluplife.controllers.item import ItemController
from leveluplife.controllers.user import UserController
from leveluplife.models.error import (
    ItemAlreadyExistsError,
    ItemNotFoundError,
    ItemNameNotFoundError,
    ItemAlreadyInUserError,
    ItemInUserNotFoundError,
)
from leveluplife.models.item import ItemCreate, ItemUpdate
from leveluplife.models.relationship import UserItemLinkCreate
from leveluplife.models.table import Item
from leveluplife.models.user import UserCreate, Tribe


@pytest.mark.asyncio
async def test_create_item(
    item_controller: ItemController, session: Session, faker: Faker
) -> None:
    item_create = ItemCreate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        price_sell=faker.random_int(min=0, max=100),
        strength=faker.random_int(min=0, max=100),
        intelligence=faker.random_int(min=0, max=100),
        agility=faker.random_int(min=0, max=100),
        wise=faker.random_int(min=0, max=100),
        psycho=faker.random_int(min=0, max=100),
    )
    # Act
    result = await item_controller.create_item(item_create)

    item = session.exec(select(Item).where(Item.id == result.id)).one()

    # Assert
    assert result.name == item_create.name == item.name
    assert result.description == item_create.description == item.description
    assert result.price_sell == item_create.price_sell == item.price_sell
    assert result.strength == item_create.strength == item.strength
    assert result.intelligence == item_create.intelligence == item.intelligence
    assert result.agility == item_create.agility == item.agility
    assert result.wise == item_create.wise == item.wise
    assert result.psycho == item_create.psycho == item.psycho


@pytest.mark.asyncio
async def test_create_item_already_exists_error(
    item_controller: ItemController, faker: Faker
) -> None:
    # Prepare
    item_create = ItemCreate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        price_sell=faker.random_int(min=0, max=100),
        strength=faker.random_int(min=0, max=100),
        intelligence=faker.random_int(min=0, max=100),
        agility=faker.random_int(min=0, max=100),
        wise=faker.random_int(min=0, max=100),
        psycho=faker.random_int(min=0, max=100),
    )
    await item_controller.create_item(item_create)

    # Act / Assert
    with pytest.raises(ItemAlreadyExistsError):
        await item_controller.create_item(item_create)


@pytest.mark.asyncio
async def test_get_items(item_controller: ItemController, faker: Faker) -> None:
    number_items = 5
    created_items = []
    for _ in range(number_items):
        item_create = ItemCreate(
            name=faker.unique.word(),
            description=faker.text(max_nb_chars=300),
            price_sell=faker.random_int(min=0, max=100),
            strength=faker.random_int(min=0, max=100),
            intelligence=faker.random_int(min=0, max=100),
            agility=faker.random_int(min=0, max=100),
            wise=faker.random_int(min=0, max=100),
            psycho=faker.random_int(min=0, max=100),
        )
        created_item = await item_controller.create_item(item_create)
        created_items.append(created_item)

    all_items = await item_controller.get_items(offset=0 * 20, limit=20)

    assert len(all_items) == number_items

    for i, created_item in enumerate(created_items):
        assert all_items[i].name == created_item.name
        assert all_items[i].description == created_item.description
        assert all_items[i].price_sell == created_item.price_sell
        assert all_items[i].strength == created_item.strength
        assert all_items[i].intelligence == created_item.intelligence
        assert all_items[i].agility == created_item.agility
        assert all_items[i].wise == created_item.wise
        assert all_items[i].psycho == created_item.psycho


@pytest.mark.asyncio
async def test_get_item_by_id(item_controller: ItemController, faker: Faker) -> None:
    item_create = ItemCreate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        price_sell=faker.random_int(min=0, max=100),
        strength=faker.random_int(min=0, max=100),
        intelligence=faker.random_int(min=0, max=100),
        agility=faker.random_int(min=0, max=100),
        wise=faker.random_int(min=0, max=100),
        psycho=faker.random_int(min=0, max=100),
    )

    created_item = await item_controller.create_item(item_create)

    retrieved_item = await item_controller.get_item_by_id(created_item.id)

    assert retrieved_item.name == item_create.name
    assert retrieved_item.description == item_create.description
    assert retrieved_item.price_sell == item_create.price_sell
    assert retrieved_item.strength == item_create.strength
    assert retrieved_item.intelligence == item_create.intelligence
    assert retrieved_item.agility == item_create.agility
    assert retrieved_item.wise == item_create.wise
    assert retrieved_item.psycho == item_create.psycho


@pytest.mark.asyncio
async def test_get_item_by_id_raise_item_not_found_error(
    item_controller: ItemController, faker: Faker
) -> None:
    non_existent_item_id = faker.uuid4()
    with pytest.raises(ItemNotFoundError):
        await item_controller.get_item_by_id(non_existent_item_id)


@pytest.mark.asyncio
async def test_get_item_by_name(item_controller: ItemController, faker: Faker) -> None:
    item_create = ItemCreate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        price_sell=faker.random_int(min=0, max=100),
        strength=faker.random_int(min=0, max=100),
        intelligence=faker.random_int(min=0, max=100),
        agility=faker.random_int(min=0, max=100),
        wise=faker.random_int(min=0, max=100),
        psycho=faker.random_int(min=0, max=100),
    )

    created_item = await item_controller.create_item(item_create)

    retrieved_item = await item_controller.get_item_by_name(created_item.name)

    assert retrieved_item.name == item_create.name
    assert retrieved_item.description == item_create.description
    assert retrieved_item.price_sell == item_create.price_sell
    assert retrieved_item.strength == item_create.strength
    assert retrieved_item.intelligence == item_create.intelligence
    assert retrieved_item.agility == item_create.agility
    assert retrieved_item.wise == item_create.wise
    assert retrieved_item.psycho == item_create.psycho


@pytest.mark.asyncio
async def test_get_item_by_name_raise_item_name_not_found_error(
    item_controller: ItemController, faker: Faker
) -> None:
    non_existent_item_name = faker.unique.word()
    with pytest.raises(ItemNameNotFoundError):
        await item_controller.get_item_by_name(non_existent_item_name)


@pytest.mark.asyncio
async def test_update_item(item_controller: ItemController, faker: Faker) -> None:
    item_create = ItemCreate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        price_sell=faker.random_int(min=0, max=100),
        strength=faker.random_int(min=0, max=100),
        intelligence=faker.random_int(min=0, max=100),
        agility=faker.random_int(min=0, max=100),
        wise=faker.random_int(min=0, max=100),
        psycho=faker.random_int(min=0, max=100),
    )
    new_item = await item_controller.create_item(item_create)

    item_update = ItemUpdate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        price_sell=faker.random_int(min=0, max=100),
        strength=faker.random_int(min=0, max=100),
        intelligence=faker.random_int(min=0, max=100),
        agility=faker.random_int(min=0, max=100),
        wise=faker.random_int(min=0, max=100),
        psycho=faker.random_int(min=0, max=100),
    )

    updated_item = await item_controller.update_item(new_item.id, item_update)

    assert updated_item.id == new_item.id
    assert updated_item.name == item_update.name
    assert updated_item.description == item_update.description
    assert updated_item.price_sell == item_update.price_sell
    assert updated_item.strength == item_update.strength
    assert updated_item.intelligence == item_update.intelligence
    assert updated_item.agility == item_update.agility
    assert updated_item.wise == item_update.wise
    assert updated_item.psycho == item_update.psycho


@pytest.mark.asyncio
async def test_update_item_raise_item_not_found_error(
    item_controller: ItemController, faker: Faker
) -> None:
    item_update = ItemUpdate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        price_sell=faker.random_int(min=0, max=100),
        strength=faker.random_int(min=0, max=100),
        intelligence=faker.random_int(min=0, max=100),
        agility=faker.random_int(min=0, max=100),
        wise=faker.random_int(min=0, max=100),
        psycho=faker.random_int(min=0, max=100),
    )

    nonexistent_item_id = faker.uuid4()

    with pytest.raises(ItemNotFoundError):
        await item_controller.update_item(nonexistent_item_id, item_update)


@pytest.mark.asyncio
async def test_delete_item(item_controller: ItemController, faker: Faker) -> None:
    item_create = ItemCreate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        price_sell=faker.random_int(min=0, max=100),
        strength=faker.random_int(min=0, max=100),
        intelligence=faker.random_int(min=0, max=100),
        agility=faker.random_int(min=0, max=100),
        wise=faker.random_int(min=0, max=100),
        psycho=faker.random_int(min=0, max=100),
    )
    new_item = await item_controller.create_item(item_create)

    await item_controller.delete_item(new_item.id)

    with pytest.raises(ItemNotFoundError):
        await item_controller.delete_item(new_item.id)


@pytest.mark.asyncio
async def test_delete_item_raise_item_not_found_error(
    item_controller: ItemController, faker: Faker
) -> None:
    nonexistent_item_id = faker.uuid4()

    with pytest.raises(ItemNotFoundError):
        await item_controller.delete_item(nonexistent_item_id)


@pytest.mark.asyncio
async def test_give_item_to_user(
    item_controller: ItemController, faker: Faker, user_controller: UserController
) -> None:
    # Prepare
    item_create = ItemCreate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        price_sell=faker.random_int(min=0, max=100),
        strength=faker.random_int(min=0, max=100),
        intelligence=faker.random_int(min=0, max=100),
        agility=faker.random_int(min=0, max=100),
        wise=faker.random_int(min=0, max=100),
        psycho=faker.random_int(min=0, max=100),
    )
    created_item = await item_controller.create_item(item_create)

    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )
    created_user = await user_controller.create_user(user_create)

    # Act
    await item_controller.give_item_to_user(
        created_item.id, UserItemLinkCreate(user_ids=[created_user.id])
    )

    # Assert
    retrieved_item = await item_controller.get_item_by_id(created_item.id)
    assert created_user.id in [user.id for user in retrieved_item.users]


@pytest.mark.asyncio
async def test_give_item_to_user_raise_item_already__in_user_error(
    item_controller: ItemController, faker: Faker, user_controller: UserController
) -> None:
    # Prepare
    item_create = ItemCreate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        price_sell=faker.random_int(min=0, max=100),
        strength=faker.random_int(min=0, max=100),
        intelligence=faker.random_int(min=0, max=100),
        agility=faker.random_int(min=0, max=100),
        wise=faker.random_int(min=0, max=100),
        psycho=faker.random_int(min=0, max=100),
    )
    created_item = await item_controller.create_item(item_create)

    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )
    created_user = await user_controller.create_user(user_create)

    # Act
    await item_controller.give_item_to_user(
        created_item.id, UserItemLinkCreate(user_ids=[created_user.id])
    )

    # Assert
    with pytest.raises(ItemAlreadyInUserError):
        await item_controller.give_item_to_user(
            created_item.id, UserItemLinkCreate(user_ids=[created_user.id])
        )


@pytest.mark.asyncio
async def test_give_item_to_user_raise_item_not_found_error(
    item_controller: ItemController, faker: Faker, user_controller: UserController
) -> None:
    # Prepare
    non_existent_item_id = faker.uuid4()

    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )
    created_user = await user_controller.create_user(user_create)

    user_item_link_create = UserItemLinkCreate(user_ids=[created_user.id])

    # Assert
    with pytest.raises(ItemNotFoundError):
        await item_controller.give_item_to_user(
            non_existent_item_id, user_item_link_create=user_item_link_create
        )


@pytest.mark.asyncio
async def test_remove_item_from_user(
    item_controller: ItemController, user_controller: UserController, faker: Faker
) -> None:
    # Prepare
    item_create = ItemCreate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        price_sell=faker.random_int(min=0, max=100),
        strength=faker.random_int(min=0, max=100),
        intelligence=faker.random_int(min=0, max=100),
        agility=faker.random_int(min=0, max=100),
        wise=faker.random_int(min=0, max=100),
        psycho=faker.random_int(min=0, max=100),
    )
    created_item = await item_controller.create_item(item_create)

    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )
    created_user = await user_controller.create_user(user_create)

    user_item_link_create = UserItemLinkCreate(user_ids=[created_user.id])
    await item_controller.give_item_to_user(created_item.id, user_item_link_create)

    # Act
    await item_controller.remove_item_from_user(created_item.id, created_user.id)

    # Assert
    retrieved_item = await item_controller.get_item_by_id(created_item.id)
    assert created_user.id not in [user.id for user in retrieved_item.users]


@pytest.mark.asyncio
async def test_remove_item_from_user_raise_item_in_user_not_found_error(
    item_controller: ItemController, user_controller: UserController, faker: Faker
) -> None:
    # Prepare
    item_create = ItemCreate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        price_sell=faker.random_int(min=0, max=100),
        strength=faker.random_int(min=0, max=100),
        intelligence=faker.random_int(min=0, max=100),
        agility=faker.random_int(min=0, max=100),
        wise=faker.random_int(min=0, max=100),
        psycho=faker.random_int(min=0, max=100),
    )
    created_item = await item_controller.create_item(item_create)

    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )
    created_user = await user_controller.create_user(user_create)

    user_item_link_create = UserItemLinkCreate(user_ids=[created_user.id])
    await item_controller.give_item_to_user(created_item.id, user_item_link_create)

    # Act
    await item_controller.remove_item_from_user(created_item.id, created_user.id)

    # Assert
    with pytest.raises(ItemInUserNotFoundError):
        await item_controller.remove_item_from_user(created_item.id, created_user.id)
