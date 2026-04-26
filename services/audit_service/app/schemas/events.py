from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EventEnvelope(BaseModel):
    event_id: UUID
    event_type: str
    event_version: int = Field(ge=1)
    occurred_at: datetime
    producer: str
    correlation_id: str
    payload: dict
