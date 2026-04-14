from datetime import UTC, datetime, timedelta

import jwt

from app.config.settings import get_settings


class TokenService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def create_access_token(self, *, subject: str, username: str, roles: list[str]) -> str:
        expires_at = datetime.now(UTC) + timedelta(minutes=self.settings.access_token_expire_minutes)
        payload = {
            "sub": subject,
            "username": username,
            "roles": roles,
            "type": "access",
            "exp": expires_at,
        }
        return jwt.encode(payload, self.settings.jwt_secret_key, algorithm=self.settings.jwt_algorithm)

    def create_refresh_token(self, *, subject: str) -> str:
        expires_at = datetime.now(UTC) + timedelta(days=self.settings.refresh_token_expire_days)
        payload = {
            "sub": subject,
            "type": "refresh",
            "exp": expires_at,
        }
        return jwt.encode(payload, self.settings.jwt_secret_key, algorithm=self.settings.jwt_algorithm)
