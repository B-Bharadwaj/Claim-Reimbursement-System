from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'reports_to')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'reports_to')}),
    )

    list_display = (
        'username',
        'email',
        'role',
        'reports_to',
        'is_staff',
        'is_superuser',
    )

    list_filter = ('role',)
    search_fields = ('username', 'email')
