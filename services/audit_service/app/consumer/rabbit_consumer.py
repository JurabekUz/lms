import json
import logging

import aio_pika
from pydantic import ValidationError

from app.config.settings import Settings
from app.services.ingest_service import IngestService

logger = logging.getLogger(__name__)


class RabbitConsumer:
    def __init__(self, settings: Settings, ingest_service: IngestService) -> None:
        self.settings = settings
        self.ingest_service = ingest_service
        self.connection: aio_pika.abc.AbstractRobustConnection | None = None
        self.channel: aio_pika.abc.AbstractRobustChannel | None = None
        self.queue: aio_pika.abc.AbstractQueue | None = None

    async def start(self) -> None:
        self.connection = await aio_pika.connect_robust(self.settings.rabbitmq_url)
        self.channel = await self.connection.channel()

        exchange = await self.channel.declare_exchange(
            self.settings.rabbitmq_exchange,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        dlx_exchange = await self.channel.declare_exchange(
            self.settings.rabbitmq_dlx_exchange,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )

        self.queue = await self.channel.declare_queue(
            self.settings.rabbitmq_queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": self.settings.rabbitmq_dlx_exchange,
                "x-dead-letter-routing-key": "audit",
            },
        )
        await self.queue.bind(exchange, routing_key="#")

        dlq = await self.channel.declare_queue(self.settings.rabbitmq_dlq, durable=True)
        await dlq.bind(dlx_exchange, routing_key="audit")

        await self.queue.consume(self._on_message)

    async def close(self) -> None:
        if self.channel is not None and not self.channel.is_closed:
            await self.channel.close()
        if self.connection is not None and not self.connection.is_closed:
            await self.connection.close()

    async def _on_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        async with message.process(requeue=False):
            try:
                raw = json.loads(message.body.decode("utf-8"))
            except json.JSONDecodeError as exc:
                logger.error("Malformed JSON in event body", exc_info=exc)
                raise

            try:
                inserted, event = await self.ingest_service.ingest(raw)
                if not inserted:
                    logger.info(
                        "Duplicate event ignored",
                        extra={
                            "event_id": str(event.event_id),
                            "event_type": event.event_type,
                            "correlation_id": event.correlation_id,
                        },
                    )
            except ValidationError as exc:
                logger.error("Invalid event envelope", exc_info=exc)
                raise
