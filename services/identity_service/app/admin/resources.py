from fastapi_admin.app import app as admin_app
from fastapi_admin.resources import Dropdown, Field, Model
from fastapi_admin.widgets import displays, inputs

from app.models import AdminAccount, Profile, Role, TeacherData, User


@admin_app.register
class IdentityResources(Dropdown):
    label = "Identity"
    icon = "fas fa-users-cog"

    class AdminAccountResource(Model):
        label = "Admin Accounts"
        model = AdminAccount
        fields = [
            "id",
            "username",
            Field(
                name="password",
                label="Password",
                display=displays.InputOnly(),
                input_=inputs.Password(),
            ),
            "is_active",
            "created_at",
            "updated_at",
        ]

    class RoleResource(Model):
        label = "Roles"
        model = Role
        fields = ["id", "name", "permissions", "created_at", "updated_at"]

    class UserResource(Model):
        label = "Users"
        model = User
        fields = [
            "id",
            "username",
            Field(
                name="password_hash",
                label="Password",
                display=displays.InputOnly(),
                input_=inputs.Password(),
            ),
            "email",
            "is_active",
            "roles",
            "created_at",
            "updated_at",
        ]

    class ProfileResource(Model):
        label = "Profiles"
        model = Profile
        fields = [
            "id",
            "user",
            "first_name",
            "last_name",
            "father_name",
            "bio",
            "avatar_media_id",
            "metadata",
            "created_at",
            "updated_at",
        ]

    class TeacherDataResource(Model):
        label = "Teacher Data"
        model = TeacherData
        fields = [
            "id",
            "user",
            "profession",
            "experience_years",
            "specialization",
            "created_at",
            "updated_at",
        ]

    resources = [
        AdminAccountResource,
        RoleResource,
        UserResource,
        ProfileResource,
        TeacherDataResource,
    ]
