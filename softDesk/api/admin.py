from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Project, Contributor, Issue, Comment


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'age', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'can_be_contacted', 'can_data_be_shared')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('age', 'can_be_contacted', 'can_data_be_shared')}),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'author', 'created_time')
    list_filter = ('type', 'created_time')
    search_fields = ('name', 'description')
    readonly_fields = ('created_time',)


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    list_display = ('user', 'project')
    list_filter = ('project',)


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'tag', 'priority', 'status', 'project', 'author', 'assignee', 'created_time')
    list_filter = ('tag', 'priority', 'status', 'created_time')
    search_fields = ('title', 'description')
    readonly_fields = ('created_time',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'issue', 'created_time')
    list_filter = ('created_time',)
    readonly_fields = ('created_time',)
