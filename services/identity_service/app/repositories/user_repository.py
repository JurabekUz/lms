from uuid import UUID

from app.models.user import Profile, Role, User


class UserRepository:
    async def get_by_id(self, user_id: UUID) -> User | None:
        return (
            await User.filter(id=user_id)
            .prefetch_related("roles", "profile")
            .first()
        )

    async def get_by_username(self, username: str) -> User | None:
        return (
            await User.filter(username=username)
            .prefetch_related("roles", "profile")
            .first()
        )

    async def get_by_username_or_email(self, username: str, email: str) -> User | None:
        return (
            await User.filter(username=username)
            .prefetch_related("roles", "profile")
            .first()
        ) or (
            await User.filter(email=email)
            .prefetch_related("roles", "profile")
            .first()
        )

    async def list_users(self, limit: int, offset: int) -> list[User]:
        return (
            await User.all()
            .prefetch_related("roles", "profile")
            .limit(limit)
            .offset(offset)
        )

    async def count(self) -> int:
        return await User.all().count()

    async def create(
        self,
        *,
        username: str,
        email: str,
        password_hash: str,
        is_active: bool,
        roles: list[Role],
        school_id: UUID | None,
        first_name: str,
        last_name: str,
        father_name: str | None,
        bio: str | None,
        avatar_media_id,
        metadata: dict,
    ) -> User:
        user = await User.create(
            username=username,
            email=email,
            password_hash=password_hash,
            is_active=is_active,
            school_id=school_id,
        )
        if roles:
            await user.roles.add(*roles)
        await Profile.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            father_name=father_name,
            bio=bio,
            avatar_media_id=avatar_media_id,
            metadata=metadata,
        )
        return await self.get_by_id(user.id)
