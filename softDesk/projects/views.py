from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Project, Issue, Comment
from .serializers import ProjectSerializer, IssueSerializer, CommentSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for managing projects"""
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Returns projects where the user is author or contributor
        user = self.request.user
        return Project.objects.filter(
            Q(author=user) | Q(contributors__user=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class IssueViewSet(viewsets.ModelViewSet):
    """ViewSet for managing issues"""
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Override to filter by project if project_pk is provided
        project_id = self.kwargs.get('project_pk')
        if project_id:
            return self.queryset.filter(project_id=project_id)
        return self.queryset.all()
    
    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        if project_id:
            project = get_object_or_404(Project, id=project_id)
            serializer.save(author=self.request.user, project=project)
        else:
            serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing comments"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Override to filter by issue
        issue_id = self.kwargs.get('issue_pk')
        if issue_id:
            return self.queryset.filter(issue_id=issue_id)
        return self.queryset.none()
    
    def perform_create(self, serializer):
        issue_id = self.kwargs.get('issue_pk')
        issue = get_object_or_404(Issue, id=issue_id)
        serializer.save(author=self.request.user, issue=issue)
