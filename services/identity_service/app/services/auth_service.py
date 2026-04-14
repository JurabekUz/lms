from app.exceptions import AuthenticationError
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse
from app.security.password import PasswordService
from app.security.tokens import TokenService


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
        token_service: TokenService,
    ) -> None:
        self.user_repository = user_repository
        self.password_service = password_service
        self.token_service = token_service

    async def login(self, payload: LoginRequest) -> TokenResponse:
        user = await self.user_repository.get_by_username(payload.username)
        if user is None or not user.is_active:
            raise AuthenticationError("Invalid username or password")

        if not self.password_service.verify(payload.password, user.password_hash):
            raise AuthenticationError("Invalid username or password")

        role_names = [role.name for role in user.roles]
        access_token = self.token_service.create_access_token(
            subject=str(user.id),
            username=user.username,
            roles=role_names,
        )
        refresh_token = self.token_service.create_refresh_token(subject=str(user.id))
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
