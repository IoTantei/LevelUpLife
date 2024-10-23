from sqlalchemy import Engine, create_engine
from sqlmodel import SQLModel

from leveluplife.settings import Settings


def create_app_engine():
    settings = Settings()
    engine = create_engine(settings.database_url, echo=True)
    return engine


def create_db_and_tables(engine: Engine):
    SQLModel.metadata.create_all(engine)
