import logging

from pydantic import ValidationError

from app.repositories.audit_repository import AuditRepository
from app.schemas.events import EventEnvelope

logger = logging.getLogger(__name__)


class IngestService:
    def __init__(self, audit_repository: AuditRepository) -> None:
        self.audit_repository = audit_repository

    async def ingest(self, raw_event: dict) -> tuple[bool, EventEnvelope]:
        event = EventEnvelope.model_validate(raw_event)
        inserted = await self.audit_repository.create_if_new(event)

        logger.info(
            "Event processed",
            extra={
                "event_id": str(event.event_id),
                "event_type": event.event_type,
                "correlation_id": event.correlation_id,
                "inserted": inserted,
            },
        )
        return inserted, event
