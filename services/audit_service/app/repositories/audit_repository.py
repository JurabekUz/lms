from tortoise.exceptions import IntegrityError

from app.models import AuditEvent
from app.schemas.events import EventEnvelope


class AuditRepository:
    async def create_if_new(self, event: EventEnvelope) -> bool:
        try:
            await AuditEvent.create(
                event_id=event.event_id,
                event_type=event.event_type,
                event_version=event.event_version,
                occurred_at=event.occurred_at,
                producer=event.producer,
                correlation_id=event.correlation_id,
                payload=event.payload,
            )
            return True
        except IntegrityError:
            return False
