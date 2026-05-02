import asyncio
import logging
from datetime import datetime, timezone

from app.infra.event_publisher import EventPublisher
from app.models.outbox import OutboxEvent
from app.events.envelope import EventEnvelope

logger = logging.getLogger(__name__)

class OutboxWorker:
    """
    Background Worker: Bazadagi yuborilmagan eventlarni RabbitMQ'ga chiqaradi.
    Bu "Guaranteed Delivery"ni ta'minlaydi.
    """
    def __init__(self, publisher: EventPublisher, interval_seconds: int = 5) -> None:
        self.publisher = publisher
        self.interval_seconds = interval_seconds
        self._should_run = True

    async def run(self) -> None:
        logger.info("Outbox worker started")
        while self._should_run:
            try:
                await self._process_events()
            except Exception as e:
                logger.error(f"Error in outbox worker: {e}")
            
            await asyncio.sleep(self.interval_seconds)

    def stop(self) -> None:
        self._should_run = False

    async def _process_events(self) -> None:
        # Hali yuborilmagan (processed_at is null) eventlarni olamiz.
        events = await OutboxEvent.filter(processed_at__isnull=True).all()
        
        if not events:
            return

        logger.info(f"Processing {len(events)} outbox events")

        for event_model in events:
            try:
                # Envelope ni JSON dan EventEnvelope obyektiga aylantiramiz.
                envelope = EventEnvelope(**event_model.payload)
                
                # RabbitMQ ga yuboramiz.
                await self.publisher.publish(envelope)
                
                # Agar muvaffaqiyatli ketsa, bazada "yuborildi" deb belgilaymiz.
                event_model.processed_at = datetime.now(timezone.utc)
                await event_model.save()
                
                logger.info(f"Event {event_model.id} processed and sent to MQ")
            except Exception as e:
                # Agar RabbitMQ o'chgan bo'lsa, bu xato beradi va keyingi safar yana urinib ko'riladi.
                logger.error(f"Failed to process outbox event {event_model.id}: {e}")
