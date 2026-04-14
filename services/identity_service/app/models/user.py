from fastapi_admin.models import AbstractAdmin
from tortoise import fields, signals
from tortoise.models import Model


class TimestampMixin:
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class Role(Model, TimestampMixin):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=50, unique=True)
    permissions = fields.JSONField(default=dict)

    class Meta:
        table = "roles"


class User(Model, TimestampMixin):
    id = fields.UUIDField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    password_hash = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)

    roles: fields.ManyToManyRelation[Role] = fields.ManyToManyField(
        "models.Role",
        related_name="users",
        through="user_roles",
    )

    class Meta:
        table = "users"


@signals.pre_save(User)
async def hash_user_password(_, instance: User, using_db, update_fields) -> None:
    from app.security.password import PasswordService

    password_service = PasswordService()
    if instance.pk:
        db_user = await User.get_or_none(pk=instance.pk)
        if db_user and db_user.password_hash != instance.password_hash and not _is_hashed(instance.password_hash):
            instance.password_hash = password_service.hash(instance.password_hash)
        return

    if instance.password_hash and not _is_hashed(instance.password_hash):
        instance.password_hash = password_service.hash(instance.password_hash)


class Profile(Model, TimestampMixin):
    id = fields.UUIDField(pk=True)
    user = fields.OneToOneField("models.User", related_name="profile", on_delete=fields.CASCADE)
    first_name = fields.CharField(max_length=100)
    last_name = fields.CharField(max_length=100)
    father_name = fields.CharField(max_length=100, null=True)
    bio = fields.TextField(null=True)
    avatar_media_id = fields.UUIDField(null=True)
    metadata = fields.JSONField(default=dict)

    class Meta:
        table = "profiles"


class TeacherData(Model, TimestampMixin):
    id = fields.UUIDField(pk=True)
    user = fields.OneToOneField(
        "models.User",
        related_name="teacher_data",
        on_delete=fields.CASCADE,
    )
    profession = fields.CharField(max_length=255)
    experience_years = fields.IntField(default=0)
    specialization = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "teacher_data"


class AdminAccount(AbstractAdmin, TimestampMixin):
    id = fields.UUIDField(pk=True)
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "admin_accounts"


def _is_hashed(value: str | None) -> bool:
    return bool(value and value.startswith("$2"))
