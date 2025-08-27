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
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsProjectAuthor]
        else:
            permission_classes = [IsAuthenticated, IsProjectContributor]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        # Returns projects where the user is author or contributor
        user = self.request.user
        from accounts.models import Contributor
        return Project.objects.filter(
            Q(author=user) | Q(contributors__user=user)
        ).distinct().select_related('author')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Store project details before deletion for the response message
        project_name = instance.name
        project_id = instance.id
        
        # Perform deletion
        self.perform_destroy(instance)
        
        # Return a success message
        return Response({
            "detail": f"Project '{project_name}' (ID: {project_id}) has been successfully deleted."
        }, status=status.HTTP_200_OK)


class IssueViewSet(viewsets.ModelViewSet):
    """ViewSet for managing issues"""
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsProjectContributor, IsAuthorOrReadOnly, CanAssignToProjectContributors]
    
    def handle_exception(self, exc):
        # Customize handling of invalid primary key errors
        if isinstance(exc, ValidationError) and getattr(exc, 'detail', {}).get('assignee'):
            # Customize error message for assignments
            return Response(
                {'assignee': str(exc.detail['assignee'][0])},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)
    
    def get_queryset(self):
        # Returns issues from projects where the user is a contributor
        user = self.request.user
        from accounts.models import Contributor
        user_projects = Project.objects.filter(
            Q(author=user) | Q(contributors__user=user)
        ).distinct()
        
        # Use select_related to prefetch related author and assignee
        # and project to avoid N+1 queries
        base_queryset = self.queryset.select_related('author', 'assignee', 'project')
        
        project_id = self.kwargs.get('project_pk')
        if project_id:
            # Filter by specific project
            return base_queryset.filter(
                project_id=project_id,
                project__in=user_projects
            )
        
        # Return all issues from user's projects
        return base_queryset.filter(project__in=user_projects)
    
    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk') or self.request.data.get('project')
        if project_id:
            project = get_object_or_404(Project, id=project_id)
            
            # Check if an assignee is provided
            assignee_id = self.request.data.get('assignee')
            if assignee_id:
                # Explicitly check if the user is a contributor to the project
                from accounts.models import Contributor, User
                try:
                    assignee = User.objects.get(pk=assignee_id)
                    if not Contributor.objects.filter(project=project, user=assignee).exists():
                        raise ValidationError({
                            "assignee": f"User {assignee.username} (ID: {assignee_id}) is not a contributor to project '{project.name}'."
                        })
                except User.DoesNotExist:
                    raise ValidationError({
                        "assignee": f"User with ID {assignee_id} does not exist."
                    })
            
            serializer.save(author=self.request.user, project=project)
        else:
            raise ValidationError({"project": "This field is required."})
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Store issue details before deletion for the response message
        issue_title = instance.title
        project_name = instance.project.name
        issue_id = instance.id
        
        # Perform deletion
        self.perform_destroy(instance)
        
        # Return a success message
        return Response({
            "detail": f"Issue '{issue_title}' (ID: {issue_id}) from project '{project_name}' has been successfully deleted."
        }, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing comments"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsProjectContributor, IsAuthorOrReadOnly]
    
    def handle_exception(self, exc):
        # Customize handling of invalid primary key errors
        if isinstance(exc, ValidationError) and getattr(exc, 'detail', {}).get('assignee'):
            # Customize error message for assignments
            return Response(
                {'assignee': str(exc.detail['assignee'][0])},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)
    
    def get_queryset(self):
        # Returns comments from issues of projects where the user is a contributor
        user = self.request.user
        from accounts.models import Contributor
        user_projects = Project.objects.filter(
            Q(author=user) | Q(contributors__user=user)
        ).distinct()
        
        # Use select_related to prefetch related author and issue to avoid N+1 queries
        base_queryset = self.queryset.select_related('author', 'issue', 'issue__project')
        
        issue_id = self.kwargs.get('issue_pk')
        if issue_id:
            # Filter by specific issue
            return base_queryset.filter(
                issue_id=issue_id,
                issue__project__in=user_projects
            )
        
        # Return all comments from user's projects
        return base_queryset.filter(issue__project__in=user_projects)
    
    def perform_create(self, serializer):
        issue_id = self.kwargs.get('issue_pk') or self.request.data.get('issue')
        if issue_id:
            issue = get_object_or_404(Issue, id=issue_id)
            
            serializer.save(author=self.request.user, issue=issue)
        else:
            raise ValidationError({"issue": "This field is required."})
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Store comment details before deletion for the response message
        comment_id = instance.id
        issue_title = instance.issue.title
        project_name = instance.issue.project.name
        
        # Perform deletion
        self.perform_destroy(instance)
        
        # Return a success message
        return Response({
            "detail": f"Comment (ID: {comment_id}) on issue '{issue_title}' from project '{project_name}' has been successfully deleted."
        }, status=status.HTTP_200_OK)
