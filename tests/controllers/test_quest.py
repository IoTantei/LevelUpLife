from datetime import datetime

import pytest
from faker import Faker
from sqlmodel import select, Session
import random
from leveluplife.controllers.quest import QuestController
from leveluplife.controllers.user import UserController
from leveluplife.models.error import (
    QuestAlreadyExistsError,
    QuestNotFoundError,
    QuestAlreadyInUserError,
    QuestInUserNotFoundError,
)
from leveluplife.models.quest import QuestCreate, Type, QuestUpdate
from leveluplife.models.relationship import UserQuestLinkCreate, QuestStatus
from leveluplife.models.table import Quest
from leveluplife.models.user import UserCreate, Tribe


@pytest.mark.asyncio
async def test_create_quest(
    quest_controller: QuestController, session: Session, faker: Faker
) -> None:
    quest_create = QuestCreate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        type=Type("daily"),
    )
    # Act
    result = await quest_controller.create_quest(quest_create)

    quest = session.exec(select(Quest).where(Quest.id == result.id)).one()

    # Assert
    assert result.name == quest_create.name == quest.name
    assert result.description == quest_create.description == quest.description
    assert result.type == quest_create.type == quest.type


@pytest.mark.asyncio
async def test_create_quest_already_exists_error(
    quest_controller: QuestController, faker: Faker
) -> None:
    existing_name = "existing_quest"
    existing_quest_create = QuestCreate(
        name=existing_name,
        description=faker.text(max_nb_chars=300),
        type=Type("daily"),
    )

    await quest_controller.create_quest(existing_quest_create)

    quest_create = QuestCreate(
        name=existing_name,
        description=faker.text(max_nb_chars=300),
        type=Type("daily"),
    )

    with pytest.raises(QuestAlreadyExistsError):
        await quest_controller.create_quest(quest_create)


@pytest.mark.asyncio
async def test_get_quests(quest_controller: QuestController, faker: Faker) -> None:
    number_quests = 5
    created_quests = []
    for _ in range(number_quests):
        quest_create = QuestCreate(
            name=faker.unique.word(),
            description=faker.text(max_nb_chars=300),
            type=Type("daily"),
        )
        created_quest = await quest_controller.create_quest(quest_create)
        created_quests.append(created_quest)

    all_quests = await quest_controller.get_quests(offset=0 * 20, limit=20)

    assert len(all_quests) == number_quests

    for i, created_quest in enumerate(created_quests):
        assert all_quests[i].name == created_quest.name
        assert all_quests[i].description == created_quest.description
        assert all_quests[i].type == created_quest.type


@pytest.mark.asyncio
async def test_get_quest_by_id(quest_controller: QuestController, faker: Faker) -> None:
    quest_create = QuestCreate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        type=Type("daily"),
    )

    created_quest = await quest_controller.create_quest(quest_create)

    retrieved_quest = await quest_controller.get_quest_by_id(created_quest.id)

    assert retrieved_quest.name == quest_create.name
    assert retrieved_quest.description == quest_create.description
    assert retrieved_quest.type == quest_create.type


@pytest.mark.asyncio
async def test_get_quest_by_id_raise_quest_not_found_error(
    quest_controller: QuestController, faker: Faker
) -> None:
    non_existent_quest_id = faker.uuid4()
    with pytest.raises(QuestNotFoundError):
        await quest_controller.get_quest_by_id(non_existent_quest_id)


@pytest.mark.asyncio
async def test_update_quest(quest_controller: QuestController, faker: Faker) -> None:
    quest_create = QuestCreate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        type=Type("daily"),
    )
    new_quest = await quest_controller.create_quest(quest_create)

    quest_update = QuestUpdate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        type=Type("weekly"),
    )

    updated_quest = await quest_controller.update_quest(new_quest.id, quest_update)

    assert updated_quest.id == new_quest.id
    assert updated_quest.name == quest_update.name
    assert updated_quest.description == quest_update.description
    assert updated_quest.type == quest_update.type


@pytest.mark.asyncio
async def test_update_quest_raise_item_not_found_error(
    quest_controller: QuestController, faker: Faker
) -> None:
    quest_update = QuestUpdate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        type=Type("daily"),
    )

    nonexistent_quest_id = faker.uuid4()

    with pytest.raises(QuestNotFoundError):
        await quest_controller.update_quest(nonexistent_quest_id, quest_update)


@pytest.mark.asyncio
async def test_delete_quest(quest_controller: QuestController, faker: Faker) -> None:
    quest_create = QuestCreate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        type=Type("daily"),
    )
    new_quest = await quest_controller.create_quest(quest_create)

    await quest_controller.delete_quest(new_quest.id)

    with pytest.raises(QuestNotFoundError):
        await quest_controller.delete_quest(new_quest.id)


@pytest.mark.asyncio
async def test_delete_quest_raise_quest_not_found_error(
    quest_controller: QuestController, faker: Faker
) -> None:
    nonexistent_quest_id = faker.uuid4()

    with pytest.raises(QuestNotFoundError):
        await quest_controller.delete_quest(nonexistent_quest_id)


@pytest.mark.asyncio
async def test_assign_quest_to_user(
    quest_controller: QuestController, faker: Faker, user_controller: UserController
) -> None:
    # Prepare
    quest_create = QuestCreate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        type=Type("daily"),
    )
    created_quest = await quest_controller.create_quest(quest_create)

    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )
    created_user = await user_controller.create_user(user_create)

    # Act
    await quest_controller.assign_quest_to_user(
        created_quest.id,
        UserQuestLinkCreate(user_ids=[created_user.id]),
        quest_start=datetime.now(),
        status=QuestStatus.ACTIVE,
        quest_end=None,
    )

    # Assert
    retrieved_quest = await quest_controller.get_quest_by_id(created_quest.id)
    assert created_user.id in [user.id for user in retrieved_quest.users]


@pytest.mark.asyncio
async def test_assign_quest_to_user_raise_quest_already_in_user_error(
    quest_controller: QuestController, faker: Faker, user_controller: UserController
) -> None:
    # Prepare
    quest_create = QuestCreate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        type=Type("daily"),
    )
    created_quest = await quest_controller.create_quest(quest_create)

    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )
    created_user = await user_controller.create_user(user_create)

    # Act
    await quest_controller.assign_quest_to_user(
        created_quest.id,
        UserQuestLinkCreate(user_ids=[created_user.id]),
        quest_start=datetime.now(),
        status=QuestStatus.ACTIVE,
        quest_end=None,
    )

    # Assert
    with pytest.raises(QuestAlreadyInUserError):
        await quest_controller.assign_quest_to_user(
            created_quest.id,
            UserQuestLinkCreate(user_ids=[created_user.id]),
            quest_start=datetime.now(),
            status=QuestStatus.ACTIVE,
            quest_end=None,
        )


@pytest.mark.asyncio
async def test_assign_user_to_user_raise_quest_not_found_error(
    quest_controller: QuestController, faker: Faker, user_controller: UserController
) -> None:
    # Prepare
    non_existent_quest_id = faker.uuid4()

    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )
    created_user = await user_controller.create_user(user_create)

    user_quest_link_create = UserQuestLinkCreate(user_ids=[created_user.id])

    # Assert
    with pytest.raises(QuestNotFoundError):
        await quest_controller.assign_quest_to_user(
            non_existent_quest_id,
            user_quest_link_create=user_quest_link_create,
            quest_start=datetime.now(),
            status=QuestStatus.ACTIVE,
            quest_end=None,
        )


@pytest.mark.asyncio
async def test_remove_quest_from_user(
    quest_controller: QuestController, user_controller: UserController, faker: Faker
) -> None:
    # Prepare
    quest_create = QuestCreate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        type=Type("daily"),
    )
    created_quest = await quest_controller.create_quest(quest_create)

    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )
    created_user = await user_controller.create_user(user_create)

    user_quest_link_create = UserQuestLinkCreate(user_ids=[created_user.id])
    await quest_controller.assign_quest_to_user(
        created_quest.id,
        user_quest_link_create,
        quest_start=datetime.now(),
        status=QuestStatus.ACTIVE,
        quest_end=None,
    )

    # Act
    await quest_controller.remove_quest_from_user(created_quest.id, created_user.id)

    # Assert
    retrieved_quest = await quest_controller.get_quest_by_id(created_quest.id)
    assert created_user.id not in [user.id for user in retrieved_quest.users]


@pytest.mark.asyncio
async def test_remove_quest_from_user_raise_quest_in_user_not_found_error(
    quest_controller: QuestController, user_controller: UserController, faker: Faker
) -> None:
    # Prepare
    quest_create = QuestCreate(
        name=faker.unique.word(),
        description=faker.text(max_nb_chars=300),
        type=Type("daily"),
    )
    created_quest = await quest_controller.create_quest(quest_create)

    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=random.choice(list(Tribe)),
    )
    created_user = await user_controller.create_user(user_create)

    user_quest_link_create = UserQuestLinkCreate(user_ids=[created_user.id])
    await quest_controller.assign_quest_to_user(
        created_quest.id,
        user_quest_link_create,
        quest_start=datetime.now(),
        status=QuestStatus.ACTIVE,
        quest_end=None,
    )

    # Act
    await quest_controller.remove_quest_from_user(created_quest.id, created_user.id)

    # Assert
    with pytest.raises(QuestInUserNotFoundError):
        await quest_controller.remove_quest_from_user(created_quest.id, created_user.id)
