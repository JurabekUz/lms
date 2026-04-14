from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.security.password import PasswordService
from app.security.tokens import TokenService
from app.services.auth_service import AuthService
from app.services.user_service import UserService


def get_user_service() -> UserService:
    return UserService(user_repository=UserRepository(), role_repository=RoleRepository())


def get_auth_service() -> AuthService:
    return AuthService(
        user_repository=UserRepository(),
        password_service=PasswordService(),
        token_service=TokenService(),
    )
