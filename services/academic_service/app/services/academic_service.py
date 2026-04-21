from uuid import UUID

from app.exceptions import ConflictError, NotFoundError, ValidationError
from app.models import AcademicYear, ClassStudent, SchoolClass, Semester, Subject
from app.repositories import (
    AcademicYearRepository,
    ClassStudentRepository,
    SchoolClassRepository,
    SemesterRepository,
    SubjectRepository,
)
from app.schemas import (
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


class AcademicService:
    def __init__(
        self,
        academic_year_repository: AcademicYearRepository,
        semester_repository: SemesterRepository,
        subject_repository: SubjectRepository,
        school_class_repository: SchoolClassRepository,
        class_student_repository: ClassStudentRepository,
    ) -> None:
        self.academic_year_repository = academic_year_repository
        self.semester_repository = semester_repository
        self.subject_repository = subject_repository
        self.school_class_repository = school_class_repository
        self.class_student_repository = class_student_repository

    async def create_academic_year(self, payload: AcademicYearCreateRequest, *, school_id: UUID) -> AcademicYearResponse:
        self._validate_date_range(payload.start_date, payload.end_date, "Academic year")
        academic_year = await self.academic_year_repository.create(school_id=school_id, **payload.model_dump())
        return self._serialize_academic_year(academic_year)

    async def list_academic_years(self, *, school_id: UUID) -> list[AcademicYearResponse]:
        items = await self.academic_year_repository.list_all(school_id=school_id)
        return [self._serialize_academic_year(item) for item in items]

    async def create_semester(self, payload: SemesterCreateRequest, *, school_id: UUID) -> SemesterResponse:
        self._validate_date_range(payload.start_date, payload.end_date, "Semester")
        academic_year = await self.academic_year_repository.get_by_id(payload.academic_year_id)
        if academic_year is None:
            raise NotFoundError("Academic year not found")
        if academic_year.school_id != school_id:
            raise NotFoundError("Academic year not found")
        if payload.start_date < academic_year.start_date or payload.end_date > academic_year.end_date:
            raise ValidationError("Semester dates must be within the academic year")
        if await self.semester_repository.overlaps(payload.academic_year_id, payload.start_date, payload.end_date):
            raise ConflictError("Semester dates overlap an existing semester")

        semester = await self.semester_repository.create(**payload.model_dump())
        return self._serialize_semester(semester)

    async def list_semesters(self, *, school_id: UUID) -> list[SemesterResponse]:
        items = await self.semester_repository.list_all(school_id=school_id)
        return [self._serialize_semester(item) for item in items]

    async def create_subject(self, payload: SubjectCreateRequest, *, school_id: UUID) -> SubjectResponse:
        subject = await self.subject_repository.create(school_id=school_id, **payload.model_dump())
        return self._serialize_subject(subject)

    async def list_subjects(self, *, school_id: UUID) -> list[SubjectResponse]:
        items = await self.subject_repository.list_all(school_id=school_id)
        return [self._serialize_subject(item) for item in items]

    async def create_class(self, payload: SchoolClassCreateRequest, *, school_id: UUID) -> SchoolClassResponse:
        school_class = await self.school_class_repository.create(school_id=school_id, **payload.model_dump())
        return self._serialize_school_class(school_class)

    async def list_classes(self, *, school_id: UUID) -> list[SchoolClassResponse]:
        items = await self.school_class_repository.list_all(school_id=school_id)
        return [self._serialize_school_class(item) for item in items]

    async def assign_student_to_class(
        self,
        class_id: UUID,
        payload: ClassStudentAssignRequest,
        *,
        school_id: UUID,
    ) -> ClassStudentResponse:
        school_class = await self.school_class_repository.get_by_id(class_id, school_id=school_id)
        if school_class is None:
            raise NotFoundError("Class not found")
        if await self.class_student_repository.exists(class_id=class_id, student_id=payload.student_id):
            raise ConflictError("Student is already assigned to this class")

        class_student = await self.class_student_repository.create(
            school_class_id=class_id,
            student_id=payload.student_id,
        )
        return self._serialize_class_student(class_student)

    async def list_class_students(self, class_id: UUID, *, school_id: UUID) -> list[ClassStudentResponse]:
        school_class = await self.school_class_repository.get_by_id(class_id, school_id=school_id)
        if school_class is None:
            raise NotFoundError("Class not found")
        items = await self.class_student_repository.list_by_class(class_id)
        return [self._serialize_class_student(item) for item in items]

    @staticmethod
    def _validate_date_range(start_date, end_date, entity_name: str) -> None:
        if start_date >= end_date:
            raise ValidationError(f"{entity_name} start_date must be before end_date")

    @staticmethod
    def _serialize_academic_year(item: AcademicYear) -> AcademicYearResponse:
        return AcademicYearResponse(
            id=item.id,
            name=item.name,
            start_date=item.start_date,
            end_date=item.end_date,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    @staticmethod
    def _serialize_semester(item: Semester) -> SemesterResponse:
        return SemesterResponse(
            id=item.id,
            academic_year_id=item.academic_year_id,
            name=item.name,
            start_date=item.start_date,
            end_date=item.end_date,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    @staticmethod
    def _serialize_subject(item: Subject) -> SubjectResponse:
        return SubjectResponse(
            id=item.id,
            name=item.name,
            type=item.type,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    @staticmethod
    def _serialize_school_class(item: SchoolClass) -> SchoolClassResponse:
        return SchoolClassResponse(
            id=item.id,
            name=item.name,
            grade_level=item.grade_level,
            room_number=item.room_number,
            homeroom_teacher_id=item.homeroom_teacher_id,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    @staticmethod
    def _serialize_class_student(item: ClassStudent) -> ClassStudentResponse:
        return ClassStudentResponse(
            id=item.id,
            school_class_id=item.school_class_id,
            student_id=item.student_id,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
