from uuid import UUID

from app.repositories.school_repository import SchoolRepository
from app.schemas.school import (
    SchoolCreateRequest,
    SchoolResponse,
    SchoolListResponse,
)

class SchoolService:
    def __init__(self, school_repository: SchoolRepository) -> None:
        self.school_repository = school_repository
    
    async def get_by_id(self, school_id: UUID) -> SchoolResponse:
        school = await self.school_repository.get_or_404(school_id)
        return SchoolResponse.model_validate(school)

    async def get_list(self, limit: int, offset: int) -> SchoolListResponse:
        schools = await self.school_repository.list(limit=limit, offset=offset)
        return SchoolListResponse(
            items=[SchoolResponse.model_validate(school) for school in schools],
            total=await self.school_repository.count(),
            limit=limit,
            offset=offset,
        )

    async def create(self, payload: SchoolCreateRequest) -> SchoolResponse:
        print(payload)
        print(payload.name)
        print(type(payload))
        school = await self.school_repository.create(name=payload.name)
        return SchoolResponse.model_validate(school)