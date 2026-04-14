from uuid import UUID

from app.exceptions import ConflictError, NotFoundError
from app.models.user import Role, User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    UserCreateRequest,
    UserListResponse,
    UserProfileResponse,
    UserResponse,
)
from app.security.password import PasswordService


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
    ) -> None:
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.password_service = PasswordService()

    async def create_user(self, payload: UserCreateRequest) -> UserResponse:
        existing_user = await self.user_repository.get_by_username_or_email(
            username=payload.username,
            email=payload.email,
        )
        if existing_user is not None:
            raise ConflictError("Username or email already exists")

        roles = await self._resolve_roles(payload.roles)
        user = await self.user_repository.create(
            username=payload.username,
            email=payload.email,
            password_hash=self.password_service.hash(payload.password),
            is_active=payload.is_active,
            roles=roles,
            first_name=payload.first_name,
            last_name=payload.last_name,
            father_name=payload.father_name,
            bio=payload.bio,
            avatar_media_id=payload.avatar_media_id,
            metadata=payload.metadata,
        )
        return self._serialize_user(user)

    async def get_user(self, user_id: UUID) -> UserResponse:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return self._serialize_user(user)

    async def list_users(self, limit: int, offset: int) -> UserListResponse:
        users = await self.user_repository.list_users(limit=limit, offset=offset)
        total = await self.user_repository.count()
        return UserListResponse(
            items=[self._serialize_user(user) for user in users],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def _resolve_roles(self, role_names: list[str]) -> list[Role]:
        if not role_names:
            return []

        roles = await self.role_repository.get_by_names(role_names)
        if len(roles) != len(set(role_names)):
            raise NotFoundError("One or more roles do not exist")
        return roles

    @staticmethod
    def _serialize_user(user: User) -> UserResponse:
        profile = getattr(user, "profile", None)
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            roles=[role.name for role in user.roles],
            profile=UserProfileResponse(
                first_name=profile.first_name if profile else "",
                last_name=profile.last_name if profile else "",
                father_name=profile.father_name if profile else None,
                bio=profile.bio if profile else None,
                avatar_media_id=profile.avatar_media_id if profile else None,
                metadata=profile.metadata if profile else {},
            ),
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
