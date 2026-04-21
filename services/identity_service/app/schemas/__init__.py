from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.common import HealthResponse
from app.schemas.user import UserCreateRequest, UserListResponse, UserProfileResponse, UserResponse
from app.schemas.school import SchoolCreateRequest, SchoolListResponse, SchoolResponse

__all__ = [
    "HealthResponse",
    "LoginRequest",
    "TokenResponse",
    "UserCreateRequest",
    "UserListResponse",
    "UserProfileResponse",
    "UserResponse",
    "SchoolCreateRequest",
    "SchoolResponse",
    "SchoolListResponse",
]
