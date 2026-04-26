import logging
from abc import ABC, abstractmethod
from typing import Any

from app.events.envelope import EventEnvelope

logger = logging.getLogger(__name__)


class EventPublisher(ABC):
    """
    Service layer uchun umumiy publisher interface.

    Nima uchun kerak:
    - UserService RabbitMQ kutubxonasiga to'g'ridan-to'g'ri bog'lanmasin.
    - Istalgan implementatsiyani almashtirish oson bo'lsin (Rabbit/Noop/test fake).
    """

    @abstractmethod
    async def publish(self, event: EventEnvelope) -> None:
        raise NotImplementedError


class NoopEventPublisher(EventPublisher):
    """
    Rabbit ishlamasa ham API yiqilib ketmasligi uchun fallback publisher.
    Event yubormaydi, faqat warning log yozadi.
    """

    async def publish(self, event: EventEnvelope) -> None:
        logger.warning(
            "Skipping event publish because publisher is disabled",
            extra={
                "event_id": str(event.event_id),
                "event_type": event.event_type,
                "correlation_id": event.correlation_id,
            },
        )


class RabbitMQEventPublisher(EventPublisher):
    """
    EventEnvelope ni RabbitMQ exchange ga yuboradigan real publisher.
    Oqim: connect() -> publish(...) -> close().
    """

    def __init__(self, *, url: str, exchange_name: str) -> None:
        self.url = url
        self.exchange_name = exchange_name
        self._connection: Any | None = None
        self._channel: Any | None = None
        self._exchange: Any | None = None

    async def connect(self) -> None:
        # Lazy import: test/paytda aio_pika o'rnatilmagan bo'lsa ham modul importi yiqilmaydi.
        import aio_pika

        # Robust connection tarmoq uzilishlarida reconnect qilishga harakat qiladi.
        self._connection = await aio_pika.connect_robust(self.url)
        # Publisher confirms: broker qabul qilganini tasdiqlash uchun.
        self._channel = await self._connection.channel(publisher_confirms=True)
        # Topic exchange: routing_key orqali event type bo'yicha tarqatish.
        self._exchange = await self._channel.declare_exchange(
            self.exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )

    async def close(self) -> None:
        if self._channel is not None and not self._channel.is_closed:
            await self._channel.close()
        if self._connection is not None and not self._connection.is_closed:
            await self._connection.close()

    async def publish(self, event: EventEnvelope) -> None:
        import aio_pika

        if self._exchange is None:
            raise RuntimeError("RabbitMQ publisher is not connected")

        # Standart envelope JSON ko'rinishida yuboriladi.
        body = event.model_dump_json().encode("utf-8")
        message = aio_pika.Message(
            body=body,
            content_type="application/json",
            # message_id/event_id idempotency va tracing uchun muhim.
            message_id=str(event.event_id),
            correlation_id=event.correlation_id,
            # Persistent: broker restartida message yo'qolmasligi uchun.
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            type=event.event_type,
            headers={"event_version": event.event_version},
        )
        # routing_key sifatida event_type beriladi (masalan: identity.user.created).
        await self._exchange.publish(message=message, routing_key=event.event_type)
        logger.info(
            "Event published",
            extra={
                "event_id": str(event.event_id),
                "event_type": event.event_type,
                "correlation_id": event.correlation_id,
            },
        )
