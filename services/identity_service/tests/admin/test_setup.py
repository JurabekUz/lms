import uuid
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi_admin.utils import check_password, hash_password

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.admin.setup import SafeUsernamePasswordProvider


class FakeAdminModel:
    existing_admin = None

    @classmethod
    async def get_or_none(cls, **kwargs):
        return cls.existing_admin


class FakeRedis:
    def __init__(self):
        self.calls = []

    async def set(self, key, value, ex=None):
        self.calls.append((key, value, ex))


class FakeRequest:
    def __init__(self, form_data):
        self._form_data = form_data
        self.app = FastAPI()
        self.app.admin_path = "/admin"

    async def form(self):
        return self._form_data


@pytest.mark.asyncio
async def test_pre_save_admin_hashes_password_for_unsaved_uuid_admin():
    provider = SafeUsernamePasswordProvider(admin_model=FakeAdminModel)
    FakeAdminModel.existing_admin = None
    admin = SimpleNamespace(pk=uuid.uuid4(), password="secret123")

    await provider.pre_save_admin(None, admin, None, None)

    assert admin.password != "secret123"
    assert check_password("secret123", admin.password)


@pytest.mark.asyncio
async def test_pre_save_admin_leaves_existing_hashed_password_unchanged():
    provider = SafeUsernamePasswordProvider(admin_model=FakeAdminModel)
    existing = SimpleNamespace(password="hashed-value")
    FakeAdminModel.existing_admin = existing
    admin = SimpleNamespace(pk=uuid.uuid4(), password="hashed-value")

    await provider.pre_save_admin(None, admin, None, None)

    assert admin.password == "hashed-value"


@pytest.mark.asyncio
async def test_login_stores_admin_id_in_redis_as_string():
    provider = SafeUsernamePasswordProvider(admin_model=FakeAdminModel)
    admin_id = uuid.uuid4()
    FakeAdminModel.existing_admin = SimpleNamespace(pk=admin_id, password=hash_password("secret123"))
    request = FakeRequest({"username": "root", "password": "secret123"})
    redis = FakeRedis()

    response = await provider.login(request, redis)

    assert response.status_code == 303
    assert redis.calls
    _, stored_value, _ = redis.calls[0]
    assert stored_value == str(admin_id)
