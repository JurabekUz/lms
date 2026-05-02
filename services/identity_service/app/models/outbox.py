from tortoise import fields
from tortoise.models import Model

class OutboxEvent(Model):
    """
    Outbox Pattern uchun model. 
    Bu jadvalga eventlar asil ma'lumotlar (masalan, User) bilan bir xil tranzaksiyada yoziladi.
    Bu RabbitMQ o'chib qolsa ham event yo'qolmasligini kafolatlaydi.
    """
    id = fields.UUIDField(pk=True)
    # Event turi (masalan: identity.user.created). Tracing uchun kerak.
    event_type = fields.CharField(max_length=255)
    # Eventning to'liq JSON ko'rinishi (Envelope).
    payload = fields.JSONField()
    # Event yaratilgan vaqt.
    created_at = fields.DatetimeField(auto_now_add=True)
    # RabbitMQ'ga muvaffaqiyatli yuborilgan vaqt. Agar null bo'lsa - hali yuborilmagan.
    processed_at = fields.DatetimeField(null=True)

    class Meta:
        table = "outbox_events"
