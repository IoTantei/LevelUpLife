import pytest
from faker import Faker
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel
from starlette.testclient import TestClient
from testcontainers.postgres import PostgresContainer

from leveluplife.api import create_app
from leveluplife.auth.utils import get_current_active_user
from leveluplife.controllers.comment import CommentController
from leveluplife.controllers.item import ItemController
from leveluplife.controllers.quest import QuestController
from leveluplife.controllers.rating import RatingController
from leveluplife.controllers.reaction import ReactionController
from leveluplife.controllers.task import TaskController
from leveluplife.controllers.user import UserController
from main import lifespan


@pytest.fixture(name="faker")
def get_faker() -> Faker:
    return Faker("fr_FR")


@pytest.fixture(name="postgres", scope="session", autouse=True)
def generate_test_pgsql():
    with PostgresContainer("postgres:latest") as postgres:
        postgres.with_env("POSTGRES_USER", "test")
        postgres.with_env("POSTGRES_PASSWORD", "testpassword")
        postgres.with_env("POSTGRES_DB", "testdb")
        yield postgres


@pytest.fixture(name="engine", scope="session", autouse=True)
def fixture_engine(postgres):
    engine = create_engine(postgres.get_connection_url())
    SQLModel.metadata.create_all(engine)
    yield engine


@pytest.fixture(name="session")
def fixture_session(engine) -> Session:
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True)
def clear_db(engine):
    yield
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


@pytest.fixture(name="user_controller")
def get_user_controller(session: Session) -> UserController:
    return UserController(session)


@pytest.fixture(name="task_controller")
def get_task_controller(session: Session) -> TaskController:
    return TaskController(session)


@pytest.fixture(name="item_controller")
def get_item_controller(session: Session) -> ItemController:
    return ItemController(session)


@pytest.fixture(name="rating_controller")
def get_rating_controller(session: Session) -> RatingController:
    return RatingController(session)


@pytest.fixture(name="comment_controller")
def get_comment_controller(session: Session) -> CommentController:
    return CommentController(session)


@pytest.fixture(name="reaction_controller")
def get_reaction_controller(session: Session) -> ReactionController:
    return ReactionController(session)


@pytest.fixture(name="quest_controller")
def get_quest_controller(session: Session) -> QuestController:
    return QuestController(session)


@pytest.fixture(name="app")
def get_test_app() -> FastAPI:
    app = create_app(lifespan=lifespan)
    app.dependency_overrides[get_current_active_user] = lambda: "mock.jwt.token"
    return app


@pytest.fixture(name="client")
def get_test_client(app: FastAPI) -> TestClient:
    return TestClient(app)
