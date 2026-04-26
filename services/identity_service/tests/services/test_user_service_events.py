import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.schemas.user import UserCreateRequest
from app.services.user_service import UserService


def now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class FakeRole:
    name: str


@dataclass
class FakeProfile:
    first_name: str
    last_name: str
    father_name: str | None
    bio: str | None
    avatar_media_id: uuid.UUID | None
    metadata: dict


@dataclass
class FakeUser:
    id: uuid.UUID
    username: str
    email: str
    is_active: bool
    school_id: uuid.UUID | None
    roles: list[FakeRole]
    profile: FakeProfile
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)


class FakeUserRepository:
    def __init__(self):
        self.created_user: FakeUser | None = None

    async def get_by_username_or_email(self, username: str, email: str):
        return None

    async def create(self, **kwargs):
        user = FakeUser(
            id=uuid.uuid4(),
            username=kwargs["username"],
            email=kwargs["email"],
            is_active=kwargs["is_active"],
            school_id=kwargs["school_id"],
            roles=[FakeRole(name=role.name) for role in kwargs["roles"]],
            profile=FakeProfile(
                first_name=kwargs["first_name"],
                last_name=kwargs["last_name"],
                father_name=kwargs["father_name"],
                bio=kwargs["bio"],
                avatar_media_id=kwargs["avatar_media_id"],
                metadata=kwargs["metadata"],
            ),
        )
        self.created_user = user
        return user


class FakeRoleRepository:
    async def get_by_names(self, role_names: list[str]):
        return [FakeRole(name=name) for name in role_names]


class FakePublisher:
    def __init__(self):
        self.events = []

    async def publish(self, event):
        self.events.append(event)


@pytest.mark.asyncio
async def test_create_user_publishes_identity_user_created_event():
    publisher = FakePublisher()
    service = UserService(
        user_repository=FakeUserRepository(),
        role_repository=FakeRoleRepository(),
        event_publisher=publisher,
    )

    payload = UserCreateRequest(
        username="alice",
        email="alice@example.com",
        password="supersecret",
        roles=["teacher"],
        first_name="Alice",
        last_name="Doe",
    )

    result = await service.create_user(payload, correlation_id="req-123")

    assert result.username == "alice"
    assert len(publisher.events) == 1

    event = publisher.events[0]
    assert event.event_type == "identity.user.created"
    assert event.correlation_id == "req-123"
    assert event.payload["user_id"] == str(result.id)
    assert event.payload["school_id"] is None
