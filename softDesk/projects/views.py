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
from accounts.permissions import IsAuthorOrReadOnly, IsProjectContributor, IsProjectAuthor, CanAssignToProjectContributors


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for managing projects"""
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectAuthor]
    
    def get_queryset(self):
        # Returns projects where the user is author or contributor
        user = self.request.user
        from accounts.models import Contributor
        return Project.objects.filter(
            Q(author=user) | Q(contributors__user=user)
        ).distinct()
    
    def perform_create(self, serializer):
       
        serializer.save(author=self.request.user)


class IssueViewSet(viewsets.ModelViewSet):
    """ViewSet for managing issues"""
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsProjectContributor, IsAuthorOrReadOnly, CanAssignToProjectContributors]
    
    def get_queryset(self):
        # Returns issues from projects where the user is a contributor
        user = self.request.user
        from accounts.models import Contributor
        user_projects = Project.objects.filter(
            Q(author=user) | Q(contributors__user=user)
        ).distinct()
        
        project_id = self.kwargs.get('project_pk')
        if project_id:
            # Filter by specific project
            return self.queryset.filter(
                project_id=project_id,
                project__in=user_projects
            )
        
        # Return all issues from user's projects
        return self.queryset.filter(project__in=user_projects)
    
    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk') or self.request.data.get('project')
        if project_id:
            project = get_object_or_404(Project, id=project_id)
            
            serializer.save(author=self.request.user, project=project)
        else:
            raise ValidationError({"project": "This field is required."})


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing comments"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsProjectContributor, IsAuthorOrReadOnly]
    
    def get_queryset(self):
        # Returns comments from issues of projects where the user is a contributor
        user = self.request.user
        from accounts.models import Contributor
        user_projects = Project.objects.filter(
            Q(author=user) | Q(contributors__user=user)
        ).distinct()
        
        issue_id = self.kwargs.get('issue_pk')
        if issue_id:
            # Filter by specific issue
            return self.queryset.filter(
                issue_id=issue_id,
                issue__project__in=user_projects
            )
        
        # Return all comments from user's projects
        return self.queryset.filter(issue__project__in=user_projects)
    
    def perform_create(self, serializer):
        issue_id = self.kwargs.get('issue_pk') or self.request.data.get('issue')
        if issue_id:
            issue = get_object_or_404(Issue, id=issue_id)
            
            serializer.save(author=self.request.user, issue=issue)
        else:
            raise ValidationError({"issue": "This field is required."})
