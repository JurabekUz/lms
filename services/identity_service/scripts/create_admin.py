#!/usr/bin/env python
"""Script to create the first admin user."""
import asyncio
import uuid

from passlib.context import CryptContext
from tortoise import Tortoise

from app.config.settings import get_settings
from app.models import AdminAccount


_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


async def create_admin(username: str, password: str) -> None:
    """Create an admin account."""
    settings = get_settings()
    
    await Tortoise.init(
        db_url=settings.database_url,
        modules={"models": ["app.models"]},
    )
    await Tortoise.generate_schemas()
    
    hashed_password = _pwd_context.hash(password)
    
    admin = await AdminAccount.get_or_none(username=username)
    if admin:
        print(f"Admin '{username}' already exists! Updating password...")
        admin.password = hashed_password
        await admin.save()
        print(f"Password updated for '{username}'!")
        await Tortoise.close_connections()
        return
    
    admin = AdminAccount(
        id=uuid.uuid4(),
        username=username,
        password=hashed_password,
        is_active=True,
    )
    await admin.save()
    print(f"Admin '{username}' created successfully!")
    
    await Tortoise.close_connections()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python scripts/create_admin.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    asyncio.run(create_admin(username, password))
