from dataclasses import dataclass
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.repositories import (
    AcademicYearRepository,
    ClassStudentRepository,
    SchoolClassRepository,
    SemesterRepository,
    SubjectRepository,
)
from app.config.settings import get_settings
from app.services import AcademicService


@dataclass(frozen=True, slots=True)
class AuthContext:
    user_id: UUID
    username: str
    roles: list[str]
    school_id: UUID


_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_auth_context(token: str = Depends(_oauth2_scheme)) -> AuthContext:
    """
    Decode the access JWT and expose auth context to route handlers.

    We expect tokens issued by `identity-service` and shared secret/algorithm config.
    Required claims:
    - `sub`       user id (UUID)
    - `username`
    - `roles`     list[str]
    - `school_id` UUID string
    - `type`      == "access"
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

    try:
        user_id = UUID(str(payload.get("sub")))
        school_id = UUID(str(payload.get("school_id")))
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token claims") from e

    roles = payload.get("roles") or []
    if not isinstance(roles, list):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token roles")

    username = str(payload.get("username") or "")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token username")

    return AuthContext(user_id=user_id, username=username, roles=[str(r) for r in roles], school_id=school_id)


def get_academic_service() -> AcademicService:
    return AcademicService(
        academic_year_repository=AcademicYearRepository(),
        semester_repository=SemesterRepository(),
        subject_repository=SubjectRepository(),
        school_class_repository=SchoolClassRepository(),
        class_student_repository=ClassStudentRepository(),
    )
