from datetime import timedelta
from typing import Annotated

from fastapi import HTTPException, status, APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from leveluplife.auth.schemas import Token
from leveluplife.auth.utils import authenticate_user, create_access_token
from leveluplife.controllers.user import UserController
from leveluplife.dependencies import get_user_controller
from leveluplife.settings import Settings

router = APIRouter(
    prefix="/token",
    tags=["token"],
    responses={404: {"description": "Not found"}},
)

settings = Settings()


@router.post("/")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_controller: UserController = Depends(get_user_controller),
) -> Token:
    user = await authenticate_user(
        user_controller, user_username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
