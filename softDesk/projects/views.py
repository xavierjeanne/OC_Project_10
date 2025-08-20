from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Project, Issue, Comment
from .serializers import ProjectSerializer, IssueSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly, IsProjectContributor, IsProjectAuthor, CanAssignToProjectContributors


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for managing projects"""
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectAuthor]
    
    def get_queryset(self):
        # Retourne les projets où l'utilisateur est auteur ou contributeur
        user = self.request.user
        from accounts.models import Contributor
        return Project.objects.filter(
            Q(author=user) | Q(contributors__user=user)
        ).distinct()
    
    def perform_create(self, serializer):
        # L'utilisateur devient automatiquement l'auteur du projet
        # Le contributeur AUTHOR est créé automatiquement par Project.save()
        serializer.save(author=self.request.user)


class IssueViewSet(viewsets.ModelViewSet):
    """ViewSet for managing issues"""
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsProjectContributor, IsAuthorOrReadOnly, CanAssignToProjectContributors]
    
    def get_queryset(self):
        # Retourne les issues des projets où l'utilisateur est contributeur
        user = self.request.user
        from accounts.models import Contributor
        user_projects = Project.objects.filter(
            Q(author=user) | Q(contributors__user=user)
        ).distinct()
        
        project_id = self.kwargs.get('project_pk')
        if project_id:
            # Filtre par projet spécifique
            return self.queryset.filter(
                project_id=project_id,
                project__in=user_projects
            )
        
        # Retourne toutes les issues des projets de l'utilisateur
        return self.queryset.filter(project__in=user_projects)
    
    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk') or self.request.data.get('project')
        if project_id:
            project = get_object_or_404(Project, id=project_id)
            
            # Vérifier que l'utilisateur est contributeur du projet
            from accounts.models import Contributor
            if not Contributor.objects.filter(project=project, user=self.request.user).exists():
                raise ValidationError({"detail": "Vous devez être contributeur de ce projet pour créer une issue."})
            
            # Vérifier que l'assignee est un contributeur du projet si spécifié
            assignee_id = self.request.data.get('assignee')
            if assignee_id:
                if not Contributor.objects.filter(project=project, user_id=assignee_id).exists():
                    raise ValidationError({"assignee": "L'utilisateur assigné doit être un contributeur du projet."})
            
            serializer.save(author=self.request.user, project=project)
        else:
            raise ValidationError({"project": "Ce champ est requis."})


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing comments"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsProjectContributor, IsAuthorOrReadOnly]
    
    def get_queryset(self):
        # Retourne les commentaires des issues des projets où l'utilisateur est contributeur
        user = self.request.user
        from accounts.models import Contributor
        user_projects = Project.objects.filter(
            Q(author=user) | Q(contributors__user=user)
        ).distinct()
        
        issue_id = self.kwargs.get('issue_pk')
        if issue_id:
            # Filtre par issue spécifique
            return self.queryset.filter(
                issue_id=issue_id,
                issue__project__in=user_projects
            )
        
        # Retourne tous les commentaires des projets de l'utilisateur
        return self.queryset.filter(issue__project__in=user_projects)
    
    def perform_create(self, serializer):
        issue_id = self.kwargs.get('issue_pk') or self.request.data.get('issue')
        if issue_id:
            issue = get_object_or_404(Issue, id=issue_id)
            
            # Vérifier que l'utilisateur est contributeur du projet
            from accounts.models import Contributor
            if not Contributor.objects.filter(project=issue.project, user=self.request.user).exists():
                raise ValidationError({"detail": "Vous devez être contributeur de ce projet pour commenter ses issues."})
            
            serializer.save(author=self.request.user, issue=issue)
        else:
            raise ValidationError({"issue": "Ce champ est requis."})
