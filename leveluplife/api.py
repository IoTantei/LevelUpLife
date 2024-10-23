from urllib.request import Request

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette.responses import JSONResponse

from leveluplife.models.error import BaseError
from leveluplife.routes.item import router as item_router
from leveluplife.routes.task import router as task_router
from leveluplife.routes.user import router as user_router
from leveluplife.routes.rating import router as rating_router
from leveluplife.routes.auth import router as auth_router
from leveluplife.routes.comment import router as comment_router
from leveluplife.routes.reaction import router as reaction_router
from leveluplife.routes.quest import router as quest_router


def create_app(lifespan) -> FastAPI:
    origins = ["*"]
    app = FastAPI(title="LevelUpLife", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(user_router)
    app.include_router(task_router)
    app.include_router(item_router)
    app.include_router(rating_router)
    app.include_router(auth_router)
    app.include_router(comment_router)
    app.include_router(reaction_router)
    app.include_router(quest_router)

    @app.exception_handler(BaseError)
    async def exception_handler(request: Request, exc: BaseError) -> JSONResponse:
        logger.error(f"{type(exc).__name__}: {exc.message}", exc_info=exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.message,
                "name": exc.name,
                "status_code": exc.status_code,
            },
        )

    return app
