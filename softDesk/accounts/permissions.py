from rest_framework import permissions
from django.shortcuts import get_object_or_404
from .models import Contributor


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


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée qui permet seulement au propriétaire d'un objet de le modifier.
    """

    def has_object_permission(self, request, view, obj):
        # Permissions de lecture pour tous les utilisateurs authentifiés
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permissions d'écriture seulement pour le propriétaire
        # Pour le modèle User, on vérifie que c'est le même utilisateur
        return obj == request.user


class IsProjectContributor(permissions.BasePermission):
    """
    Permission qui vérifie que l'utilisateur est contributeur du projet.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Pour les actions qui nécessitent un project_pk
        project_id = view.kwargs.get('project_pk')
        if project_id:
            return Contributor.objects.filter(
                project_id=project_id,
                user=request.user
            ).exists()
        
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


class IsProjectAuthorForContributors(permissions.BasePermission):
    """
    Permission qui permet seulement à l'auteur du projet de gérer les contributeurs.
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
        # Pour les contributeurs, vérifier que l'utilisateur est l'auteur du projet
        return obj.project.author == request.user
