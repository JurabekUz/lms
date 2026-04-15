from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models import SubjectType


class AcademicYearCreateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    start_date: date
    end_date: date


class AcademicYearResponse(BaseModel):
    id: UUID
    name: str
    start_date: date
    end_date: date
    created_at: datetime
    updated_at: datetime


class SemesterCreateRequest(BaseModel):
    academic_year_id: UUID
    name: str = Field(min_length=1, max_length=100)
    start_date: date
    end_date: date


class SemesterResponse(BaseModel):
    id: UUID
    academic_year_id: UUID
    name: str
    start_date: date
    end_date: date
    created_at: datetime
    updated_at: datetime


class SubjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: SubjectType


class SubjectResponse(BaseModel):
    id: UUID
    name: str
    type: SubjectType
    created_at: datetime
    updated_at: datetime


class SchoolClassCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    grade_level: int = Field(ge=1, le=11)
    room_number: str | None = Field(default=None, max_length=20)
    homeroom_teacher_id: UUID


class SchoolClassResponse(BaseModel):
    id: UUID
    name: str
    grade_level: int
    room_number: str | None
    homeroom_teacher_id: UUID
    created_at: datetime
    updated_at: datetime


class ClassStudentAssignRequest(BaseModel):
    student_id: UUID


class ClassStudentResponse(BaseModel):
    id: UUID
    school_class_id: UUID
    student_id: UUID
    created_at: datetime
    updated_at: datetime
