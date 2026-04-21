#!/usr/bin/env python
"""Script to create a regular user (for API login)."""
import asyncio
import uuid
from tortoise import Tortoise
from passlib.context import CryptContext

from app.config.settings import get_settings
from app.models import User, Profile

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(
    username: str,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
) -> None:
    """Create a regular user for API login."""
    settings = get_settings()
    
    await Tortoise.init(
        db_url=settings.database_url,
        modules={"models": ["app.models"]},
    )
    await Tortoise.generate_schemas()
    print(password)
    
    hashed_password = _pwd_context.hash(password)
    user = await User.get_or_none(username=username)
    if user:
        print(f"User '{username}' already exists!")
        await Tortoise.close_connections()
        return
    
    user = await User.create(
        username=username,
        email=email,
        password_hash=hashed_password,
        is_active=True,
    )
    
    await Profile.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
    )
    
    print(f"User '{username}' created successfully!")
    await Tortoise.close_connections()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 6:
        print("Usage: python scripts/create_user.py <username> <email> <password> <first_name> <last_name>")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    first_name = sys.argv[4]
    last_name = sys.argv[5]
    
    asyncio.run(create_user(username, email, password, first_name, last_name))