from app.repositories import (
    AcademicYearRepository,
    ClassStudentRepository,
    SchoolClassRepository,
    SemesterRepository,
    SubjectRepository,
)
from app.services import AcademicService


def get_academic_service() -> AcademicService:
    return AcademicService(
        academic_year_repository=AcademicYearRepository(),
        semester_repository=SemesterRepository(),
        subject_repository=SubjectRepository(),
        school_class_repository=SchoolClassRepository(),
        class_student_repository=ClassStudentRepository(),
    )
