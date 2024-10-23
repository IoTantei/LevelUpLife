from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from leveluplife.auth.hash import verify_password
from leveluplife.auth.schemas import TokenData
from leveluplife.controllers.user import UserController
from leveluplife.dependencies import get_user_controller
from leveluplife.models.table import User
from leveluplife.settings import Settings

settings = Settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_user(user_controller: UserController, user_username: str) -> User:
    return await user_controller.get_user_by_username_with_password(user_username)


async def authenticate_user(
    user_controller: UserController, user_username: str, password: str
):
    user = await get_user(user_controller, user_username)
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_controller: UserController = Depends(get_user_controller),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(user_controller, token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user
