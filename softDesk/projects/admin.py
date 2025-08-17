from django.contrib import admin
from .models import Project, Issue, Comment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'author', 'created_time')
    list_filter = ('type', 'created_time')
    search_fields = ('name', 'description')
    readonly_fields = ('created_time',)


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
