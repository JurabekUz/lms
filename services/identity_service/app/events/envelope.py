from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EventEnvelope(BaseModel):
    event_id: UUID
    event_type: str
    event_version: int = Field(default=1, ge=1)
    occurred_at: datetime
    producer: str
    correlation_id: str
    payload: dict


class IdentityUserCreatedPayload(BaseModel):
    school_id: UUID | None
    user_id: UUID
    username: str


class IdentityUserCreatedEventFactory:
    EVENT_TYPE = "identity.user.created"

    @classmethod
    def build(cls, *, correlation_id: str, school_id: UUID | None, user_id: UUID, username: str) -> EventEnvelope:
        payload = IdentityUserCreatedPayload(
            school_id=school_id,
            user_id=user_id,
            username=username,
        )
        return EventEnvelope(
            event_id=uuid4(),
            event_type=cls.EVENT_TYPE,
            event_version=1,
            occurred_at=datetime.now(timezone.utc),
            producer="identity-service",
            correlation_id=correlation_id,
            payload=payload.model_dump(mode="json"),
        )
