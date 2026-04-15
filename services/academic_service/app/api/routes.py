from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_academic_service
from app.schemas import (
    AcademicYearCreateRequest,
    AcademicYearResponse,
    ClassStudentAssignRequest,
    ClassStudentResponse,
    HealthResponse,
    SchoolClassCreateRequest,
    SchoolClassResponse,
    SemesterCreateRequest,
    SemesterResponse,
    SubjectCreateRequest,
    SubjectResponse,
)
from app.services import AcademicService

router = APIRouter()
system_router = APIRouter(tags=["system"])
academic_router = APIRouter(tags=["academic"])


@system_router.get("/health", response_model=HealthResponse)
async def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok", service="academic-service")


@system_router.get("/ready", response_model=HealthResponse)
async def readiness() -> HealthResponse:
    return HealthResponse(status="ready", service="academic-service")


@academic_router.post("/academic-years", response_model=AcademicYearResponse, status_code=status.HTTP_201_CREATED)
async def create_academic_year(
    payload: AcademicYearCreateRequest,
    academic_service: AcademicService = Depends(get_academic_service),
) -> AcademicYearResponse:
    return await academic_service.create_academic_year(payload)


@academic_router.get("/academic-years", response_model=list[AcademicYearResponse], status_code=status.HTTP_200_OK)
async def list_academic_years(
    academic_service: AcademicService = Depends(get_academic_service),
) -> list[AcademicYearResponse]:
    return await academic_service.list_academic_years()


@academic_router.post("/semesters", response_model=SemesterResponse, status_code=status.HTTP_201_CREATED)
async def create_semester(
    payload: SemesterCreateRequest,
    academic_service: AcademicService = Depends(get_academic_service),
) -> SemesterResponse:
    return await academic_service.create_semester(payload)


@academic_router.get("/semesters", response_model=list[SemesterResponse], status_code=status.HTTP_200_OK)
async def list_semesters(
    academic_service: AcademicService = Depends(get_academic_service),
) -> list[SemesterResponse]:
    return await academic_service.list_semesters()


@academic_router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    payload: SubjectCreateRequest,
    academic_service: AcademicService = Depends(get_academic_service),
) -> SubjectResponse:
    return await academic_service.create_subject(payload)


@academic_router.get("/subjects", response_model=list[SubjectResponse], status_code=status.HTTP_200_OK)
async def list_subjects(
    academic_service: AcademicService = Depends(get_academic_service),
) -> list[SubjectResponse]:
    return await academic_service.list_subjects()


@academic_router.post("/classes", response_model=SchoolClassResponse, status_code=status.HTTP_201_CREATED)
async def create_class(
    payload: SchoolClassCreateRequest,
    academic_service: AcademicService = Depends(get_academic_service),
) -> SchoolClassResponse:
    return await academic_service.create_class(payload)


@academic_router.get("/classes", response_model=list[SchoolClassResponse], status_code=status.HTTP_200_OK)
async def list_classes(
    academic_service: AcademicService = Depends(get_academic_service),
) -> list[SchoolClassResponse]:
    return await academic_service.list_classes()


@academic_router.post(
    "/classes/{class_id}/students",
    response_model=ClassStudentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_student_to_class(
    class_id: UUID,
    payload: ClassStudentAssignRequest,
    academic_service: AcademicService = Depends(get_academic_service),
) -> ClassStudentResponse:
    return await academic_service.assign_student_to_class(class_id, payload)


@academic_router.get(
    "/classes/{class_id}/students",
    response_model=list[ClassStudentResponse],
    status_code=status.HTTP_200_OK,
)
async def list_class_students(
    class_id: UUID,
    academic_service: AcademicService = Depends(get_academic_service),
) -> list[ClassStudentResponse]:
    return await academic_service.list_class_students(class_id)


router.include_router(system_router)
router.include_router(academic_router)
