import pytest
from faker import Faker
from sqlmodel import Session, select

from leveluplife.controllers.reaction import ReactionController
from leveluplife.controllers.task import TaskController
from leveluplife.controllers.user import UserController
from leveluplife.models.error import ReactionAlreadyExistsError, ReactionNotFoundError
from leveluplife.models.reaction import ReactionCreate, ReactionType, ReactionUpdate
from leveluplife.models.table import Reaction
from leveluplife.models.task import TaskCreate
from leveluplife.models.user import UserCreate, Tribe


@pytest.mark.asyncio
async def test_create_reaction(
    task_controller: TaskController,
    user_controller: UserController,
    reaction_controller: ReactionController,
    session: Session,
    faker: Faker,
) -> None:
    # Prepare
    user_create = UserCreate(
        username=faker.unique.user_name(),
        email=faker.unique.email(),
        password=faker.password(),
        tribe=Tribe.NOSFERATI,
    )
    user = await user_controller.create_user(user_create)

    task_create = TaskCreate(
        title=faker.unique.word(),
        description=faker.text(max_nb_chars=400),
        completed=faker.boolean(),
        category=faker.word(),
        user_id=user.id,
    )
    task = await task_controller.create_task(task_create)

    reaction_create = ReactionCreate(
        task_id=task.id,
        user_id=user.id,
        reaction=ReactionType("👍"),
    )

    # Act
    result = await reaction_controller.create_reaction(reaction_create)

    reaction = session.exec(select(Reaction).where(Reaction.id == result.id)).one()

    # Assert
    assert result.reaction == reaction_create.reaction == reaction.reaction
    assert result.task_id == reaction_create.task_id == reaction.task_id
    assert result.user_id == reaction_create.user_id == reaction.user_id


@pytest.mark.asyncio
async def test_create_reaction_already_exists_error(
    task_controller: TaskController,
    user_controller: UserController,
    reaction_controller: ReactionController,
    faker: Faker,
) -> None:
    user_create = UserCreate(
        username=faker.unique.user_name(),
        email=faker.unique.email(),
        password=faker.password(),
        tribe=Tribe.NOSFERATI,
    )
    user = await user_controller.create_user(user_create)

    task_create = TaskCreate(
        title=faker.unique.word(),
        description=faker.text(max_nb_chars=400),
        completed=faker.boolean(),
        category=faker.word(),
        user_id=user.id,
    )
    task = await task_controller.create_task(task_create)

    reaction_create = ReactionCreate(
        task_id=task.id,
        user_id=user.id,
        reaction=ReactionType("👍"),
    )

    # Act
    await reaction_controller.create_reaction(reaction_create)

    # Assert
    with pytest.raises(ReactionAlreadyExistsError):
        await reaction_controller.create_reaction(reaction_create)


@pytest.mark.asyncio
async def test_get_reactions(
    reaction_controller: ReactionController,
    user_controller: UserController,
    task_controller: TaskController,
    faker: Faker,
) -> None:
    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=Tribe.NOSFERATI,
    )
    user = await user_controller.create_user(user_create)

    number_reactions = 5
    created_reactions = []
    for _ in range(number_reactions):
        task_create = TaskCreate(
            title=faker.unique.word(),
            description=faker.text(max_nb_chars=400),
            completed=faker.boolean(),
            category=faker.word(),
            user_id=user.id,
        )
        task = await task_controller.create_task(task_create)

        reaction_create = ReactionCreate(
            task_id=task.id,
            user_id=user.id,
            reaction=ReactionType("👍"),
        )
        created_reaction = await reaction_controller.create_reaction(reaction_create)
        created_reactions.append(created_reaction)

    all_reactions = await reaction_controller.get_reactions(offset=0 * 20, limit=20)

    assert len(all_reactions) == number_reactions

    for i, created_reaction in enumerate(created_reactions):
        assert all_reactions[i].task_id == created_reaction.task_id
        assert all_reactions[i].user_id == created_reaction.user_id
        assert all_reactions[i].reaction == created_reaction.reaction


@pytest.mark.asyncio
async def test_get_reaction_by_id(
    task_controller: TaskController,
    user_controller: UserController,
    reaction_controller: ReactionController,
    faker: Faker,
) -> None:
    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=Tribe.NOSFERATI,
    )
    user = await user_controller.create_user(user_create)

    task_create = TaskCreate(
        title=faker.unique.word(),
        description=faker.text(max_nb_chars=400),
        completed=faker.boolean(),
        category=faker.word(),
        user_id=user.id,
    )
    task = await task_controller.create_task(task_create)

    reaction_create = ReactionCreate(
        task_id=task.id,
        user_id=user.id,
        reaction=ReactionType("👍"),
    )
    created_reaction = await reaction_controller.create_reaction(reaction_create)

    retrieved_reaction = await reaction_controller.get_reaction_by_id(
        created_reaction.id
    )

    assert retrieved_reaction.task_id == created_reaction.task_id
    assert retrieved_reaction.user_id == created_reaction.user_id
    assert retrieved_reaction.reaction == created_reaction.reaction


@pytest.mark.asyncio
async def test_get_reaction_by_id_raise_reaction_not_found_error(
    reaction_controller: ReactionController,
    faker: Faker,
) -> None:
    non_existent_reaction_id = faker.uuid4()
    with pytest.raises(ReactionNotFoundError):
        await reaction_controller.get_reaction_by_id(non_existent_reaction_id)


@pytest.mark.asyncio
async def test_update_reaction(
    reaction_controller: ReactionController,
    user_controller: UserController,
    task_controller: TaskController,
    faker: Faker,
) -> None:
    user_create = UserCreate(
        username=faker.unique.user_name(),
        email=faker.unique.email(),
        password=faker.password(),
        tribe=Tribe.NOSFERATI,
    )
    user = await user_controller.create_user(user_create)

    task_create = TaskCreate(
        title=faker.unique.word(),
        description=faker.text(max_nb_chars=400),
        completed=faker.boolean(),
        category=faker.word(),
        user_id=user.id,
    )
    task = await task_controller.create_task(task_create)

    reaction_create = ReactionCreate(
        task_id=task.id,
        user_id=user.id,
        reaction=ReactionType("👍"),
    )
    created_reaction = await reaction_controller.create_reaction(reaction_create)

    reaction_update = ReactionUpdate(
        reaction=ReactionType("🥰"),
    )

    updated_reaction = await reaction_controller.update_reaction(
        created_reaction.id, reaction_update
    )

    assert updated_reaction.id == created_reaction.id
    assert updated_reaction.task_id == created_reaction.task_id
    assert updated_reaction.user_id == created_reaction.user_id
    assert updated_reaction.reaction == created_reaction.reaction


@pytest.mark.asyncio
async def test_update_reaction_raise_reaction_not_found_error(
    reaction_controller: ReactionController, faker: Faker
) -> None:
    reaction_update = ReactionUpdate(
        reaction=ReactionType("👍"),
    )

    nonexistent_reaction_id = faker.uuid4()

    with pytest.raises(ReactionNotFoundError):
        await reaction_controller.update_reaction(
            nonexistent_reaction_id, reaction_update
        )


@pytest.mark.asyncio
async def test_delete_reaction(
    reaction_controller: ReactionController,
    user_controller: UserController,
    task_controller: TaskController,
    faker: Faker,
) -> None:
    user_create = UserCreate(
        username=faker.unique.user_name(),
        email=faker.unique.email(),
        password=faker.password(),
        tribe=Tribe.NOSFERATI,
    )
    user = await user_controller.create_user(user_create)

    task_create = TaskCreate(
        title=faker.unique.word(),
        description=faker.text(max_nb_chars=400),
        completed=faker.boolean(),
        category=faker.word(),
        user_id=user.id,
    )
    task = await task_controller.create_task(task_create)

    reaction_create = ReactionCreate(
        task_id=task.id,
        user_id=user.id,
        reaction=ReactionType("👍"),
    )
    created_reaction = await reaction_controller.create_reaction(reaction_create)

    await reaction_controller.delete_reaction(created_reaction.id)

    with pytest.raises(ReactionNotFoundError):
        await reaction_controller.delete_reaction(created_reaction.id)


@pytest.mark.asyncio
async def test_delete_reaction_raise_reaction_not_found_error(
    reaction_controller: ReactionController, faker: Faker
) -> None:
    nonexistent_reaction_id = faker.uuid4()

    with pytest.raises(ReactionNotFoundError):
        await reaction_controller.delete_reaction(nonexistent_reaction_id)
