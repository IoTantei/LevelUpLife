import pytest
from faker import Faker
from sqlmodel import Session, select

from leveluplife.controllers.task import TaskController
from leveluplife.controllers.user import UserController
from leveluplife.models.error import (
    TaskAlreadyExistsError,
    TaskNotFoundError,
    TaskTitleNotFoundError,
)
from leveluplife.models.table import Task
from leveluplife.models.task import TaskCreate, TaskUpdate
from leveluplife.models.user import Tribe, UserCreate


@pytest.mark.asyncio
async def test_create_task(
    task_controller: TaskController,
    user_controller: UserController,
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
    # Act
    result = await task_controller.create_task(task_create)

    task = session.exec(select(Task).where(Task.id == result.id)).one()

    # Assert
    assert result.title == task_create.title == task.title
    assert result.description == task_create.description == task.description
    assert result.completed == task_create.completed == task.completed
    assert result.category == task_create.category == task.category
    assert result.user_id == task_create.user_id == task.user_id


@pytest.mark.asyncio
async def test_create_task_already_exists_error(
    task_controller: TaskController, user_controller: UserController, faker: Faker
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

    # Act
    await task_controller.create_task(task_create)

    # Assert
    with pytest.raises(TaskAlreadyExistsError):
        await task_controller.create_task(task_create)


@pytest.mark.asyncio
async def test_get_tasks(
    task_controller: TaskController, user_controller: UserController, faker: Faker
) -> None:
    user_create = UserCreate(
        username=faker.unique.user_name()[:18],
        email=faker.unique.email(),
        password=faker.password(),
        tribe=Tribe.NOSFERATI,
    )
    user = await user_controller.create_user(user_create)

    number_tasks = 5
    created_tasks = []
    for _ in range(number_tasks):
        task_create = TaskCreate(
            title=faker.unique.word(),
            description=faker.text(max_nb_chars=400),
            completed=faker.boolean(),
            category=faker.word(),
            user_id=user.id,
        )
        created_task = await task_controller.create_task(task_create)
        created_tasks.append(created_task)

    all_tasks = await task_controller.get_tasks(offset=0 * 20, limit=20)

    assert len(all_tasks) == number_tasks

    for i, created_task in enumerate(created_tasks):
        assert all_tasks[i].title == created_task.title
        assert all_tasks[i].description == created_task.description
        assert all_tasks[i].completed == created_task.completed
        assert all_tasks[i].category == created_task.category
        assert all_tasks[i].user_id == created_task.user_id


@pytest.mark.asyncio
async def test_get_task_by_id(
    task_controller: TaskController, user_controller: UserController, faker: Faker
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

    created_task = await task_controller.create_task(task_create)

    retrieved_task = await task_controller.get_task_by_id(created_task.id)

    assert retrieved_task.title == task_create.title
    assert retrieved_task.description == task_create.description
    assert retrieved_task.completed == task_create.completed
    assert retrieved_task.category == task_create.category
    assert retrieved_task.user_id == user.id


@pytest.mark.asyncio
async def test_get_task_by_id_raise_task_not_found_error(
    task_controller: TaskController, faker: Faker
) -> None:
    non_existent_task_id = faker.uuid4()
    with pytest.raises(TaskNotFoundError):
        await task_controller.get_task_by_id(non_existent_task_id)


@pytest.mark.asyncio
async def test_get_task_by_title(
    task_controller: TaskController, user_controller: UserController, faker: Faker
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

    created_task = await task_controller.create_task(task_create)

    retrieved_task = await task_controller.get_task_by_title(created_task.title)

    assert retrieved_task.title == task_create.title
    assert retrieved_task.description == task_create.description
    assert retrieved_task.completed == task_create.completed
    assert retrieved_task.category == task_create.category
    assert retrieved_task.user_id == user.id


@pytest.mark.asyncio
async def test_get_task_by_title_raise_task_title_not_found_error(
    task_controller: TaskController, faker: Faker
) -> None:
    non_existent_task_title = faker.text()
    with pytest.raises(TaskTitleNotFoundError):
        await task_controller.get_task_by_title(non_existent_task_title)


@pytest.mark.asyncio
async def test_update_task(
    task_controller: TaskController, user_controller: UserController, faker: Faker
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
    new_task = await task_controller.create_task(task_create)

    task_update = TaskUpdate(
        title=faker.unique.word(),
        description=faker.text(max_nb_chars=400),
        completed=faker.boolean(),
        category=faker.word(),
    )

    updated_task = await task_controller.update_task(new_task.id, task_update)

    assert updated_task.id == new_task.id
    assert updated_task.title == task_update.title
    assert updated_task.description == task_update.description
    assert updated_task.completed == task_update.completed
    assert updated_task.category == task_update.category
    assert updated_task.user_id == user.id


@pytest.mark.asyncio
async def test_update_task_raise_task_not_found_error(
    task_controller: TaskController, faker: Faker
) -> None:
    task_update = TaskUpdate(
        title=faker.unique.word(),
        description=faker.text(max_nb_chars=400),
        completed=faker.boolean(),
        category=faker.word(),
    )

    nonexistent_task_id = faker.uuid4()

    with pytest.raises(TaskNotFoundError):
        await task_controller.update_task(nonexistent_task_id, task_update)


@pytest.mark.asyncio
async def test_delete_task(
    task_controller: TaskController, user_controller: UserController, faker: Faker
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
    new_task = await task_controller.create_task(task_create)

    await task_controller.delete_task(new_task.id)

    with pytest.raises(TaskNotFoundError):
        await task_controller.delete_task(new_task.id)


@pytest.mark.asyncio
async def test_delete_task_raise_task_not_found_error(
    task_controller: TaskController, faker: Faker
) -> None:
    nonexistent_task_id = faker.uuid4()

    with pytest.raises(TaskNotFoundError):
        await task_controller.delete_task(nonexistent_task_id)
