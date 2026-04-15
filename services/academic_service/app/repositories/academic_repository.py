from datetime import date
from uuid import UUID

from tortoise.expressions import Q

from app.models import AcademicYear, ClassStudent, SchoolClass, Semester, Subject


class AcademicYearRepository:
    async def create(self, **kwargs) -> AcademicYear:
        return await AcademicYear.create(**kwargs)

    async def list_all(self) -> list[AcademicYear]:
        return await AcademicYear.all().order_by("-start_date")

    async def get_by_id(self, academic_year_id: UUID) -> AcademicYear | None:
        return await AcademicYear.get_or_none(id=academic_year_id)


class SemesterRepository:
    async def create(self, **kwargs) -> Semester:
        return await Semester.create(**kwargs)

    async def list_all(self, academic_year_id: UUID | None = None) -> list[Semester]:
        query = Semester.all().select_related("academic_year").order_by("start_date")
        if academic_year_id is not None:
            query = query.filter(academic_year_id=academic_year_id)
        return await query

    async def get_by_id(self, semester_id: UUID) -> Semester | None:
        return await Semester.get_or_none(id=semester_id).select_related("academic_year")

    async def overlaps(self, academic_year_id: UUID, start_date: date, end_date: date) -> bool:
        return await Semester.filter(
            academic_year_id=academic_year_id,
        ).filter(
            Q(start_date__lte=end_date) & Q(end_date__gte=start_date)
        ).exists()


class SubjectRepository:
    async def create(self, **kwargs) -> Subject:
        return await Subject.create(**kwargs)

    async def list_all(self) -> list[Subject]:
        return await Subject.all().order_by("name", "type")

    async def get_by_id(self, subject_id: UUID) -> Subject | None:
        return await Subject.get_or_none(id=subject_id)


class SchoolClassRepository:
    async def create(self, **kwargs) -> SchoolClass:
        return await SchoolClass.create(**kwargs)

    async def list_all(self) -> list[SchoolClass]:
        return await SchoolClass.all().order_by("grade_level", "name")

    async def get_by_id(self, class_id: UUID) -> SchoolClass | None:
        return await SchoolClass.get_or_none(id=class_id)


class ClassStudentRepository:
    async def create(self, **kwargs) -> ClassStudent:
        return await ClassStudent.create(**kwargs)

    async def exists(self, class_id: UUID, student_id: UUID) -> bool:
        return await ClassStudent.filter(school_class_id=class_id, student_id=student_id).exists()

    async def list_by_class(self, class_id: UUID) -> list[ClassStudent]:
        return await ClassStudent.filter(school_class_id=class_id).order_by("created_at")
