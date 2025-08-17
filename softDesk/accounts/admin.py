from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Contributor


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'age', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'can_be_contacted', 'can_data_be_shared')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('age', 'can_be_contacted', 'can_data_be_shared')}),
    )


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    list_display = ('user', 'project')
    list_filter = ('project',)
