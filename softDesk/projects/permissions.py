from rest_framework import permissions
from django.db.models import Q
from accounts.models import Contributor


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée qui permet seulement aux auteurs d'un objet de le modifier.
    Les autres utilisateurs authentifiés peuvent seulement le lire.
    """

    def has_object_permission(self, request, view, obj):
        # Permissions de lecture pour tous les utilisateurs authentifiés
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permissions d'écriture seulement pour l'auteur de l'objet
        return obj.author == request.user


class IsProjectContributor(permissions.BasePermission):
    """
    Permission qui vérifie que l'utilisateur est contributeur du projet.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return True

    def has_object_permission(self, request, view, obj):
        # Vérifier que l'utilisateur est contributeur du projet associé à l'objet
        if hasattr(obj, 'project'):
            project = obj.project
        elif hasattr(obj, 'issue'):
            project = obj.issue.project
        else:
            # Si l'objet est un Project
            project = obj

        return Contributor.objects.filter(
            project=project,
            user=request.user
        ).exists()


class CanAssignToProjectContributors(permissions.BasePermission):
    """
    Permission pour vérifier que l'assigned_to dans une Issue est un contributeur du projet.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Vérifier lors de la création/modification d'une issue
        if request.method in ['POST', 'PUT', 'PATCH']:
            assigned_to_id = request.data.get('assigned_to')
            project_id = request.data.get('project')
            
            if assigned_to_id and project_id:
                # Vérifier que l'utilisateur assigné est contributeur du projet
                return Contributor.objects.filter(
                    project_id=project_id,
                    user_id=assigned_to_id
                ).exists()
        
        return True


class IsProjectAuthor(permissions.BasePermission):
    """
    Permission qui permet seulement à l'auteur du projet de faire des modifications.
    """

    def has_object_permission(self, request, view, obj):
        # Permissions de lecture pour tous les contributeurs
        if request.method in permissions.SAFE_METHODS:
            return Contributor.objects.filter(
                project=obj,
                user=request.user
            ).exists()

        # Permissions d'écriture seulement pour l'auteur
        return obj.author == request.user
