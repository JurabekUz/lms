import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.services.ingest_service import IngestService


class FakeAuditRepository:
    def __init__(self):
        self.seen: set[uuid.UUID] = set()

    async def create_if_new(self, event):
        if event.event_id in self.seen:
            return False
        self.seen.add(event.event_id)
        return True


def build_event(event_id: uuid.UUID | None = None) -> dict:
    return {
        "event_id": str(event_id or uuid.uuid4()),
        "event_type": "identity.user.created",
        "event_version": 1,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "producer": "identity-service",
        "correlation_id": str(uuid.uuid4()),
        "payload": {
            "school_id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "username": "alice",
        },
    }


@pytest.mark.asyncio
async def test_ingest_accepts_valid_event():
    service = IngestService(audit_repository=FakeAuditRepository())

    inserted, event = await service.ingest(build_event())

    assert inserted is True
    assert event.event_type == "identity.user.created"


@pytest.mark.asyncio
async def test_ingest_is_idempotent_for_duplicate_event_id():
    repository = FakeAuditRepository()
    service = IngestService(audit_repository=repository)
    shared_event_id = uuid.uuid4()

    first_inserted, _ = await service.ingest(build_event(shared_event_id))
    second_inserted, _ = await service.ingest(build_event(shared_event_id))

    assert first_inserted is True
    assert second_inserted is False


@pytest.mark.asyncio
async def test_ingest_rejects_invalid_envelope():
    service = IngestService(audit_repository=FakeAuditRepository())

    with pytest.raises(ValidationError):
        await service.ingest({"event_type": "identity.user.created"})
