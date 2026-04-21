from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config.settings import get_settings
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.security.password import PasswordService
from app.security.tokens import TokenService
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.repositories.school_repository import SchoolRepository
from app.services.school_service import SchoolService

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(_oauth2_scheme)) -> User:
    """
    Resolve the currently authenticated user from the `Authorization: Bearer ...` token.

    - Decodes the JWT using `settings.jwt_secret_key`
    - Ensures token is an access token (`payload.type == "access"`)
    - Loads the user from DB and ensures it's active
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired") from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    subject = payload.get("sub")
    try:
        user_id = UUID(str(subject))
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject") from e

    user = await UserRepository().get_by_id(user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


def get_user_service() -> UserService:
    return UserService(user_repository=UserRepository(), role_repository=RoleRepository())


def get_auth_service() -> AuthService:
    return AuthService(
        user_repository=UserRepository(),
        password_service=PasswordService(),
        token_service=TokenService(),
    )

def get_school_service():
    return SchoolService(school_repository=SchoolRepository())
