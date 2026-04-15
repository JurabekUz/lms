from app.schemas.academic import (
    AcademicYearCreateRequest,
    AcademicYearResponse,
    ClassStudentAssignRequest,
    ClassStudentResponse,
    SchoolClassCreateRequest,
    SchoolClassResponse,
    SemesterCreateRequest,
    SemesterResponse,
    SubjectCreateRequest,
    SubjectResponse,
)
from app.schemas.common import HealthResponse

__all__ = [
    "HealthResponse",
    "AcademicYearCreateRequest",
    "AcademicYearResponse",
    "SemesterCreateRequest",
    "SemesterResponse",
    "SubjectCreateRequest",
    "SubjectResponse",
    "SchoolClassCreateRequest",
    "SchoolClassResponse",
    "ClassStudentAssignRequest",
    "ClassStudentResponse",
]
