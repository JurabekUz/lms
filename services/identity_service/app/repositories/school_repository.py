from uuid import UUID

from app.models import School
from app.exceptions import NotFoundError

class SchoolRepository:

    async def get_by_id(self, school_id: UUID) -> School | None:
        return await School.filter(id=school_id).first()
    
    async def get_or_404(self, school_id: UUID) -> School:
        school = await self.get_by_id(school_id)
        if school is None:
            raise NotFoundError("School not found")
        return school

    async def create(self, name: str) -> School:
        return await School.create(name=name)
    
    async def list(self, limit: int, offset: int) -> list[School]:
        return await School.all().limit(limit).offset(offset)
    
    async def count(self) -> int:
        return await School.all().count()