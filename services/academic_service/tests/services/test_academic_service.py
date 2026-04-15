import sys
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.exceptions import ConflictError, NotFoundError, ValidationError
from app.models import SubjectType
from app.schemas import (
    AcademicYearCreateRequest,
    ClassStudentAssignRequest,
    SchoolClassCreateRequest,
    SemesterCreateRequest,
    SubjectCreateRequest,
)
from app.services import AcademicService


def now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class FakeAcademicYear:
    id: uuid.UUID
    name: str
    start_date: date
    end_date: date
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)


@dataclass
class FakeSemester:
    id: uuid.UUID
    academic_year_id: uuid.UUID
    name: str
    start_date: date
    end_date: date
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)


@dataclass
class FakeSubject:
    id: uuid.UUID
    name: str
    type: SubjectType
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)


@dataclass
class FakeSchoolClass:
    id: uuid.UUID
    name: str
    grade_level: int
    room_number: str | None
    homeroom_teacher_id: uuid.UUID
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)


@dataclass
class FakeClassStudent:
    id: uuid.UUID
    school_class_id: uuid.UUID
    student_id: uuid.UUID
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)


class FakeAcademicYearRepository:
    def __init__(self):
        self.items = {}

    async def create(self, **kwargs):
        item = FakeAcademicYear(id=uuid.uuid4(), **kwargs)
        self.items[item.id] = item
        return item

    async def list_all(self):
        return list(self.items.values())

    async def get_by_id(self, academic_year_id):
        return self.items.get(academic_year_id)


class FakeSemesterRepository:
    def __init__(self):
        self.items = []
        self.should_overlap = False

    async def create(self, **kwargs):
        item = FakeSemester(id=uuid.uuid4(), **kwargs)
        self.items.append(item)
        return item

    async def list_all(self, academic_year_id=None):
        if academic_year_id is None:
            return list(self.items)
        return [item for item in self.items if item.academic_year_id == academic_year_id]

    async def overlaps(self, academic_year_id, start_date, end_date):
        return self.should_overlap


class FakeSubjectRepository:
    def __init__(self):
        self.items = []

    async def create(self, **kwargs):
        item = FakeSubject(id=uuid.uuid4(), **kwargs)
        self.items.append(item)
        return item

    async def list_all(self):
        return list(self.items)


class FakeSchoolClassRepository:
    def __init__(self):
        self.items = {}

    async def create(self, **kwargs):
        item = FakeSchoolClass(id=uuid.uuid4(), **kwargs)
        self.items[item.id] = item
        return item

    async def list_all(self):
        return list(self.items.values())

    async def get_by_id(self, class_id):
        return self.items.get(class_id)


class FakeClassStudentRepository:
    def __init__(self):
        self.items = []
        self.duplicate = False

    async def create(self, **kwargs):
        item = FakeClassStudent(id=uuid.uuid4(), **kwargs)
        self.items.append(item)
        return item

    async def exists(self, class_id, student_id):
        return self.duplicate

    async def list_by_class(self, class_id):
        return [item for item in self.items if item.school_class_id == class_id]


def build_service():
    return AcademicService(
        academic_year_repository=FakeAcademicYearRepository(),
        semester_repository=FakeSemesterRepository(),
        subject_repository=FakeSubjectRepository(),
        school_class_repository=FakeSchoolClassRepository(),
        class_student_repository=FakeClassStudentRepository(),
    )


@pytest.mark.asyncio
async def test_create_academic_year_rejects_invalid_dates():
    service = build_service()

    with pytest.raises(ValidationError):
        await service.create_academic_year(
            AcademicYearCreateRequest(
                name="2026-2027",
                start_date=date(2026, 9, 1),
                end_date=date(2026, 9, 1),
            )
        )


@pytest.mark.asyncio
async def test_create_semester_rejects_dates_outside_academic_year():
    service = build_service()
    academic_year = await service.academic_year_repository.create(
        name="2026-2027",
        start_date=date(2026, 9, 1),
        end_date=date(2027, 6, 1),
    )

    with pytest.raises(ValidationError):
        await service.create_semester(
            SemesterCreateRequest(
                academic_year_id=academic_year.id,
                name="Fall",
                start_date=date(2026, 8, 1),
                end_date=date(2026, 12, 1),
            )
        )


@pytest.mark.asyncio
async def test_create_semester_rejects_overlap():
    service = build_service()
    academic_year = await service.academic_year_repository.create(
        name="2026-2027",
        start_date=date(2026, 9, 1),
        end_date=date(2027, 6, 1),
    )
    service.semester_repository.should_overlap = True

    with pytest.raises(ConflictError):
        await service.create_semester(
            SemesterCreateRequest(
                academic_year_id=academic_year.id,
                name="Fall",
                start_date=date(2026, 9, 1),
                end_date=date(2026, 12, 20),
            )
        )


@pytest.mark.asyncio
async def test_assign_student_to_class_requires_existing_class():
    service = build_service()

    with pytest.raises(NotFoundError):
        await service.assign_student_to_class(uuid.uuid4(), ClassStudentAssignRequest(student_id=uuid.uuid4()))


@pytest.mark.asyncio
async def test_assign_student_to_class_rejects_duplicates():
    service = build_service()
    school_class = await service.create_class(
        SchoolClassCreateRequest(
            name="7-A",
            grade_level=7,
            room_number="201",
            homeroom_teacher_id=uuid.uuid4(),
        )
    )
    service.class_student_repository.duplicate = True

    with pytest.raises(ConflictError):
        await service.assign_student_to_class(
            school_class.id,
            ClassStudentAssignRequest(student_id=uuid.uuid4()),
        )


@pytest.mark.asyncio
async def test_create_subject_supports_schedule_categories():
    service = build_service()

    subject = await service.create_subject(
        SubjectCreateRequest(name="Lunch", type=SubjectType.MEAL)
    )

    assert subject.name == "Lunch"
    assert subject.type == SubjectType.MEAL
