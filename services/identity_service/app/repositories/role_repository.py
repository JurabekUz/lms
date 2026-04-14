from app.models.user import Role


class RoleRepository:
    async def get_by_names(self, role_names: list[str]) -> list[Role]:
        return await Role.filter(name__in=role_names).all()
