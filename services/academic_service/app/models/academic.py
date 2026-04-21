from enum import StrEnum

from tortoise import fields
from tortoise.models import Model


class TimestampMixin:
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class SubjectType(StrEnum):
    REGULAR = "REGULAR"
    EXTRACURRICULAR = "EXTRACURRICULAR"
    MEAL = "MEAL"


class AcademicYear(Model, TimestampMixin):
    id = fields.UUIDField(pk=True)
    school_id = fields.UUIDField()
    name = fields.CharField(max_length=50, unique=True)
    start_date = fields.DateField()
    end_date = fields.DateField()

    class Meta:
        table = "academic_years"


class Semester(Model, TimestampMixin):
    id = fields.UUIDField(pk=True)
    academic_year = fields.ForeignKeyField(
        "models.AcademicYear",
        related_name="semesters",
        on_delete=fields.CASCADE,
    )
    name = fields.CharField(max_length=100)
    start_date = fields.DateField()
    end_date = fields.DateField()

    class Meta:
        table = "semesters"
        unique_together = (("academic_year_id", "name"),)


class Subject(Model, TimestampMixin):
    id = fields.UUIDField(pk=True)
    school_id = fields.UUIDField()
    name = fields.CharField(max_length=100)
    type = fields.CharEnumField(SubjectType, max_length=32)

    class Meta:
        table = "subjects"
        unique_together = (("name", "type"),)


class SchoolClass(Model, TimestampMixin):
    id = fields.UUIDField(pk=True)
    school_id = fields.UUIDField()
    name = fields.CharField(max_length=50)
    grade_level = fields.IntField()
    room_number = fields.CharField(max_length=20, null=True)
    homeroom_teacher_id = fields.UUIDField()

    class Meta:
        table = "classes"
        unique_together = (("name", "grade_level"),)


class ClassStudent(Model, TimestampMixin):
    id = fields.UUIDField(pk=True)
    school_class = fields.ForeignKeyField(
        "models.SchoolClass",
        related_name="students",
        on_delete=fields.CASCADE,
    )
    student_id = fields.UUIDField()

    class Meta:
        table = "class_students"
        unique_together = (("school_class_id", "student_id"),)
