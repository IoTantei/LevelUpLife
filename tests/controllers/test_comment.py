import pytest
from faker import Faker
from sqlmodel import Session, select

from leveluplife.controllers.comment import CommentController
from leveluplife.controllers.task import TaskController
from leveluplife.controllers.user import UserController
from leveluplife.models.comment import CommentCreate, CommentUpdate
from leveluplife.models.error import CommentAlreadyExistsError, CommentNotFoundError
from leveluplife.models.table import Comment
from leveluplife.models.task import TaskCreate
from leveluplife.models.user import UserCreate, Tribe


@pytest.mark.asyncio
async def test_create_comment(
    task_controller: TaskController,
    user_controller: UserController,
    comment_controller: CommentController,
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

    comment_create = CommentCreate(
        task_id=task.id,
        user_id=user.id,
        content=faker.text(max_nb_chars=800),
    )

    # Act
    result = await comment_controller.create_comment(comment_create)

    comment = session.exec(select(Comment).where(Comment.id == result.id)).one()

    # Assert
    assert result.content == comment_create.content == comment.content
    assert result.task_id == comment_create.task_id == comment.task_id
    assert result.user_id == comment_create.user_id == comment.user_id


@pytest.mark.asyncio
async def test_create_comment_already_exists_error(
    task_controller: TaskController,
    user_controller: UserController,
    comment_controller: CommentController,
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

    comment_create = CommentCreate(
        task_id=task.id,
        user_id=user.id,
        content=faker.text(max_nb_chars=800),
    )

    # Act
    await comment_controller.create_comment(comment_create)

    # Assert
    with pytest.raises(CommentAlreadyExistsError):
        await comment_controller.create_comment(comment_create)


@pytest.mark.asyncio
async def test_get_comments(
    comment_controller: CommentController,
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

    number_comments = 5
    created_comments = []
    for _ in range(number_comments):
        task_create = TaskCreate(
            title=faker.unique.word(),
            description=faker.text(max_nb_chars=400),
            completed=faker.boolean(),
            category=faker.word(),
            user_id=user.id,
        )
        task = await task_controller.create_task(task_create)

        comment_create = CommentCreate(
            task_id=task.id,
            user_id=user.id,
            content=faker.text(max_nb_chars=800),
        )
        created_comment = await comment_controller.create_comment(comment_create)
        created_comments.append(created_comment)

    all_comments = await comment_controller.get_comments(offset=0 * 20, limit=20)

    assert len(all_comments) == number_comments

    for i, created_comment in enumerate(created_comments):
        assert all_comments[i].task_id == created_comment.task_id
        assert all_comments[i].user_id == created_comment.user_id
        assert all_comments[i].content == created_comment.content


@pytest.mark.asyncio
async def test_get_comment_by_id(
    task_controller: TaskController,
    user_controller: UserController,
    comment_controller: CommentController,
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

    comment_create = CommentCreate(
        task_id=task.id,
        user_id=user.id,
        content=faker.text(max_nb_chars=800),
    )
    created_comment = await comment_controller.create_comment(comment_create)

    retrieved_comment = await comment_controller.get_comment_by_id(created_comment.id)

    assert retrieved_comment.task_id == created_comment.task_id
    assert retrieved_comment.user_id == created_comment.user_id
    assert retrieved_comment.content == created_comment.content


@pytest.mark.asyncio
async def test_get_comment_by_id_raise_comment_not_found_error(
    comment_controller: CommentController,
    faker: Faker,
) -> None:
    non_existent_comment_id = faker.uuid4()
    with pytest.raises(CommentNotFoundError):
        await comment_controller.get_comment_by_id(non_existent_comment_id)


@pytest.mark.asyncio
async def test_update_comment(
    comment_controller: CommentController,
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

    comment_create = CommentCreate(
        task_id=task.id,
        user_id=user.id,
        content=faker.text(max_nb_chars=800),
    )
    created_comment = await comment_controller.create_comment(comment_create)

    comment_update = CommentUpdate(
        content=faker.text(max_nb_chars=800),
    )

    updated_comment = await comment_controller.update_comment(
        created_comment.id, comment_update
    )

    assert updated_comment.id == created_comment.id
    assert updated_comment.task_id == created_comment.task_id
    assert updated_comment.user_id == created_comment.user_id
    assert updated_comment.content == created_comment.content


@pytest.mark.asyncio
async def test_update_comment_raise_comment_not_found_error(
    comment_controller: CommentController, faker: Faker
) -> None:
    comment_update = CommentUpdate(
        content=faker.text(max_nb_chars=800),
    )

    nonexistent_comment_id = faker.uuid4()

    with pytest.raises(CommentNotFoundError):
        await comment_controller.update_comment(nonexistent_comment_id, comment_update)


@pytest.mark.asyncio
async def test_delete_comment(
    comment_controller: CommentController,
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

    comment_create = CommentCreate(
        task_id=task.id,
        user_id=user.id,
        content=faker.text(max_nb_chars=800),
    )
    created_comment = await comment_controller.create_comment(comment_create)

    await comment_controller.delete_comment(created_comment.id)

    with pytest.raises(CommentNotFoundError):
        await comment_controller.delete_comment(created_comment.id)


@pytest.mark.asyncio
async def test_delete_comment_raise_comment_not_found_error(
    comment_controller: CommentController, faker: Faker
) -> None:
    nonexistent_comment_id = faker.uuid4()

    with pytest.raises(CommentNotFoundError):
        await comment_controller.delete_comment(nonexistent_comment_id)
