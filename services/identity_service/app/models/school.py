from tortoise import fields, Model

class School(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255, unique=True)
    address = fields.CharField(max_length=255, null=True)
    contact_email = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "schools"


