from rest_framework import permissions
from django.shortcuts import get_object_or_404
from .models import Contributor


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission that only allows authors of an object to edit it.
    Other authenticated users can only read it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for the author of the object
        return obj.author == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission that only allows the owner of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for the owner
        # For the User model, check that it's the same user
        return obj == request.user


class IsProjectContributor(permissions.BasePermission):
    """
    Permission that checks if the user is a contributor to the project.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # For actions that require a project_pk
        project_id = view.kwargs.get('project_pk')
        if project_id:
            return Contributor.objects.filter(
                project_id=project_id,
                user=request.user
            ).exists()
        
        return True

    def has_object_permission(self, request, view, obj):
        # Check that the user is a contributor to the project associated with the object
        if hasattr(obj, 'project'):
            project = obj.project
        elif hasattr(obj, 'issue'):
            project = obj.issue.project
        else:
            # If the object is a Project
            project = obj

        return Contributor.objects.filter(
            project=project,
            user=request.user
        ).exists()


class IsProjectAuthorForContributors(permissions.BasePermission):
    """
    Permission that only allows the project author to manage contributors.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        project_id = view.kwargs.get('project_pk')
        if project_id:
            from projects.models import Project
            try:
                project = Project.objects.get(id=project_id)
                return project.author == request.user
            except Project.DoesNotExist:
                return False
        
        return False

    def has_object_permission(self, request, view, obj):
        # For contributors, check that the user is the project author
        return obj.project.author == request.user


class CanAssignToProjectContributors(permissions.BasePermission):
    """
    Permission to check that the assigned_to in an Issue is a project contributor.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Check during issue creation/modification
        if request.method in ['POST', 'PUT', 'PATCH']:
            assigned_to_id = request.data.get('assigned_to')
            project_id = request.data.get('project')
            
            if assigned_to_id and project_id:
                # Check that the assigned user is a project contributor
                return Contributor.objects.filter(
                    project_id=project_id,
                    user_id=assigned_to_id
                ).exists()
        
        return True


class IsProjectAuthor(permissions.BasePermission):
    """
    Permission that only allows the project author to make modifications.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for all contributors
        if request.method in permissions.SAFE_METHODS:
            return Contributor.objects.filter(
                project=obj,
                user=request.user
            ).exists()

        # Write permissions only for the author
        return obj.author == request.user
