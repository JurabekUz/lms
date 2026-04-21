from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.schemas.school import SchoolCreateRequest, SchoolListResponse, SchoolResponse
from app.services.school_service import SchoolService
from app.api.dependencies import get_school_service

router = APIRouter(prefix="/schools", tags=["schools"])

@router.post("", response_model=SchoolResponse, status_code=status.HTTP_201_CREATED)
async def create_school(
    payload: SchoolCreateRequest, 
    school_service: SchoolService = Depends(get_school_service),
    ) -> SchoolResponse:
    return await school_service.create(payload)

@router.get("", response_model=SchoolListResponse, status_code=status.HTTP_200_OK)
async def list_schools(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    school_service: SchoolService = Depends(get_school_service),
) -> SchoolListResponse:
    return await school_service.get_list(limit=limit, offset=offset)

@router.get("/{school_id}", response_model=SchoolResponse, status_code=status.HTTP_200_OK)
async def get_school(
    school_id: UUID,
    school_service: SchoolService = Depends(get_school_service),
) -> SchoolResponse:
    return await school_service.get_by_id(school_id)

