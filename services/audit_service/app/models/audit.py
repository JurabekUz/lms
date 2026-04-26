from tortoise import fields
from tortoise.models import Model


class AuditEvent(Model):
    id = fields.UUIDField(pk=True)
    event_id = fields.UUIDField(unique=True, index=True)
    event_type = fields.CharField(max_length=255, index=True)
    event_version = fields.IntField(default=1)
    occurred_at = fields.DatetimeField()
    producer = fields.CharField(max_length=100)
    correlation_id = fields.CharField(max_length=128, index=True)
    payload = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "audit_events"
