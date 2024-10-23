from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from leveluplife.api import create_app
from leveluplife.database import create_app_engine, create_db_and_tables


@asynccontextmanager
async def lifespan(_app: FastAPI):
    engine = create_app_engine()
    create_db_and_tables(engine)
    engine.dispose()
    yield


app = create_app(lifespan=lifespan)


if __name__ == "__main__":
    uvicorn.run(app, port=7000)
