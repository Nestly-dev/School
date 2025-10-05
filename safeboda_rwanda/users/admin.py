from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Extra", {"fields": ("phone", "national_id", "district", "language")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        (None, {"fields": ("username", "email", "password1", "password2", "phone", "national_id", "district", "language")}),
    )
    list_display = ("username", "email", "phone", "is_staff", "is_superuser")
