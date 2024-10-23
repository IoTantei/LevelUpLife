import pytest
from faker import Faker
from sqlmodel import Session, select

from leveluplife.controllers.rating import RatingController
from leveluplife.controllers.task import TaskController
from leveluplife.controllers.user import UserController
from leveluplife.models.error import RatingAlreadyExistsError, RatingNotFoundError
from leveluplife.models.rating import RatingCreate, RatingUpdate
from leveluplife.models.table import Rating
from leveluplife.models.task import TaskCreate
from leveluplife.models.user import Tribe, UserCreate


@pytest.mark.asyncio
async def test_create_rating(
    task_controller: TaskController,
    user_controller: UserController,
    rating_controller: RatingController,
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

    rating_create = RatingCreate(
        task_id=task.id,
        user_id=user.id,
        rating=faker.random_int(min=0, max=10),
    )

    # Act
    result = await rating_controller.create_rating(rating_create)

    rating = session.exec(select(Rating).where(Rating.id == result.id)).one()

    # Assert
    assert result.rating == rating_create.rating == rating.rating
    assert result.task_id == rating_create.task_id == rating.task_id
    assert result.user_id == rating_create.user_id == rating.user_id


@pytest.mark.asyncio
async def test_create_rating_already_exists_error(
    task_controller: TaskController,
    user_controller: UserController,
    rating_controller: RatingController,
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

    rating_create = RatingCreate(
        task_id=task.id,
        user_id=user.id,
        rating=faker.random_int(min=0, max=10),
    )

    # Act
    await rating_controller.create_rating(rating_create)

    # Assert
    with pytest.raises(RatingAlreadyExistsError):
        await rating_controller.create_rating(rating_create)


@pytest.mark.asyncio
async def test_get_ratings(
    rating_controller: RatingController,
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

    number_ratings = 5
    created_ratings = []
    for _ in range(number_ratings):
        task_create = TaskCreate(
            title=faker.unique.word(),
            description=faker.text(max_nb_chars=400),
            completed=faker.boolean(),
            category=faker.word(),
            user_id=user.id,
        )
        task = await task_controller.create_task(task_create)

        rating_create = RatingCreate(
            task_id=task.id,
            user_id=user.id,
            rating=faker.random_int(min=0, max=10),
        )
        created_rating = await rating_controller.create_rating(rating_create)
        created_ratings.append(created_rating)

    all_ratings = await rating_controller.get_ratings(offset=0 * 20, limit=20)

    assert len(all_ratings) == number_ratings

    for i, created_rating in enumerate(created_ratings):
        assert all_ratings[i].task_id == created_rating.task_id
        assert all_ratings[i].user_id == created_rating.user_id
        assert all_ratings[i].rating == created_rating.rating


@pytest.mark.asyncio
async def test_get_rating_by_id(
    task_controller: TaskController,
    user_controller: UserController,
    rating_controller: RatingController,
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

    rating_create = RatingCreate(
        task_id=task.id,
        user_id=user.id,
        rating=faker.random_int(min=0, max=10),
    )
    created_rating = await rating_controller.create_rating(rating_create)

    retrieved_rating = await rating_controller.get_rating_by_id(created_rating.id)

    assert retrieved_rating.task_id == created_rating.task_id
    assert retrieved_rating.user_id == created_rating.user_id
    assert retrieved_rating.rating == created_rating.rating


@pytest.mark.asyncio
async def test_get_rating_by_id_raise_rating_not_found_error(
    rating_controller: RatingController,
    faker: Faker,
) -> None:
    non_existent_rating_id = faker.uuid4()
    with pytest.raises(RatingNotFoundError):
        await rating_controller.get_rating_by_id(non_existent_rating_id)


@pytest.mark.asyncio
async def test_update_rating(
    rating_controller: RatingController,
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

    rating_create = RatingCreate(
        task_id=task.id,
        user_id=user.id,
        rating=faker.random_int(min=0, max=10),
    )
    created_rating = await rating_controller.create_rating(rating_create)

    rating_update = RatingUpdate(
        rating=faker.random_int(min=0, max=10),
    )

    updated_rating = await rating_controller.update_rating(
        created_rating.id, rating_update
    )

    assert updated_rating.id == created_rating.id
    assert updated_rating.task_id == created_rating.task_id
    assert updated_rating.user_id == created_rating.user_id
    assert updated_rating.rating == rating_update.rating


@pytest.mark.asyncio
async def test_update_rating_raise_rating_not_found_error(
    rating_controller: RatingController, faker: Faker
) -> None:
    rating_update = RatingUpdate(
        rating=faker.random_int(min=0, max=10),
    )

    nonexistent_rating_id = faker.uuid4()

    with pytest.raises(RatingNotFoundError):
        await rating_controller.update_rating(nonexistent_rating_id, rating_update)


@pytest.mark.asyncio
async def test_delete_rating(
    rating_controller: RatingController,
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

    task_create = TaskCreate(
        title=faker.unique.word(),
        description=faker.text(max_nb_chars=400),
        completed=faker.boolean(),
        category=faker.word(),
        user_id=user.id,
    )
    task = await task_controller.create_task(task_create)

    rating_create = RatingCreate(
        task_id=task.id,
        user_id=user.id,
        rating=faker.random_int(min=0, max=10),
    )
    created_rating = await rating_controller.create_rating(rating_create)

    await rating_controller.delete_rating(created_rating.id)

    with pytest.raises(RatingNotFoundError):
        await rating_controller.delete_rating(created_rating.id)


@pytest.mark.asyncio
async def test_delete_rating_raise_rating_not_found_error(
    rating_controller: RatingController, faker: Faker
) -> None:
    nonexistent_rating_id = faker.uuid4()

    with pytest.raises(RatingNotFoundError):
        await rating_controller.delete_rating(nonexistent_rating_id)
