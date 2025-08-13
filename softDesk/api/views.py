from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import User, Project, Contributor, Issue, Comment
from .serializers import (
    UserSerializer, ProjectSerializer, ContributorSerializer,
    IssueSerializer, CommentSerializer
)


# User ViewSet
class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for managing users"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            # User can only view/modify their own profile
            return User.objects.filter(id=self.request.user.id)
        return User.objects.all()
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def profile(self, request):
        """Endpoint for managing the connected user's profile"""
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Project ViewSet
class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for managing projects"""
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Returns projects where the user is author or contributor
        user = self.request.user
        return Project.objects.filter(
            Q(author=user) | Q(contributor__user=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['get', 'post', 'delete'])
    def contributors(self, request, pk=None):
        """Manage project contributors"""
        project = self.get_object()
        
        if request.method == 'GET':
            contributors = Contributor.objects.filter(project=project)
            serializer = ContributorSerializer(contributors, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Check that user is the project author
            if project.author != request.user:
                return Response(
                    {"error": "Only the author can add contributors"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            user_id = request.data.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                contributor, created = Contributor.objects.get_or_create(
                    user=user, project=project
                )
                if created:
                    serializer = ContributorSerializer(contributor)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        {"error": "This user is already a contributor"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        elif request.method == 'DELETE':
            # Check that user is the project author
            if project.author != request.user:
                return Response(
                    {"error": "Only the author can remove contributors"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            user_id = request.data.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                contributor = Contributor.objects.get(user=user, project=project)
                contributor.delete()
                return Response(
                    {"message": "Contributor successfully removed"}, 
                    status=status.HTTP_204_NO_CONTENT
                )
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            except Contributor.DoesNotExist:
                return Response(
                    {"error": "This user is not a contributor to this project"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
    
    @action(detail=True, methods=['get', 'post'])
    def issues(self, request, pk=None):
        """Manage project issues"""
        project = self.get_object()
        
        if request.method == 'GET':
            issues = Issue.objects.filter(project=project)
            serializer = IssueSerializer(issues, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = IssueSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(author=request.user, project=project)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Contributor ViewSet
class ContributorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing contributors"""
    queryset = Contributor.objects.all()  # Default queryset
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Override to filter by project
        project_id = self.kwargs.get('project_pk')
        if project_id:
            return self.queryset.filter(project_id=project_id)
        return self.queryset.none()


# Issue ViewSet
class IssueViewSet(viewsets.ModelViewSet):
    """ViewSet for managing issues"""
    queryset = Issue.objects.all()  # Default queryset
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Override to filter by project
        project_id = self.kwargs.get('project_pk')
        if project_id:
            return self.queryset.filter(project_id=project_id)
        return self.queryset.none()
    
    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        project = get_object_or_404(Project, id=project_id)
        serializer.save(author=self.request.user, project=project)
    
    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None, project_pk=None):
        """Manage issue comments"""
        issue = self.get_object()
        
        if request.method == 'GET':
            comments = Comment.objects.filter(issue=issue)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(author=request.user, issue=issue)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Comment ViewSet
class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing comments"""
    queryset = Comment.objects.all()  # Default queryset
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
