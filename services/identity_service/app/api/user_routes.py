from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.dependencies import get_current_user, get_user_service
from app.schemas.user import UserCreateRequest, UserListResponse, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateRequest,
    request: Request,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    # Request object HTTP headerlarni o'qish uchun kerak.
    # `x-request-id` odatda gateway/frontend tomonidan yuboriladi; FastAPI default bermaydi.
    # Bo'lmasa biz yangi UUID beramiz: bitta so'rovni API loglari va eventlar bo'ylab kuzatish osonlashadi.
    correlation_id = request.headers.get("x-request-id", str(uuid4()))
    return await user_service.create_user(payload, correlation_id=correlation_id)


@router.get("", response_model=UserListResponse, status_code=status.HTTP_200_OK)
async def list_users(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_service: UserService = Depends(get_user_service),
) -> UserListResponse:
    return await user_service.list_users(limit=limit, offset=offset)


@router.get("/me")
async def me(
    user=Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_user(user.id)


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await user_service.get_user(user_id)
    
