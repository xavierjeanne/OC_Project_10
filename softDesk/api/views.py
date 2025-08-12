from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import User, Project, Contributor, Issue, Comment
from .serializers import (
    UserSerializer, ProjectSerializer, ContributorSerializer,
    IssueSerializer, CommentSerializer
)


# User ViewSet
class UserViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les utilisateurs"""
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
            # L'utilisateur ne peut voir/modifier que son propre profil
            return User.objects.filter(id=self.request.user.id)
        return User.objects.all()
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def profile(self, request):
        """Endpoint pour gérer le profil de l'utilisateur connecté"""
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
    """ViewSet pour gérer les projets"""
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Retourne les projets où l'utilisateur est auteur ou contributeur
        user = self.request.user
        authored_projects = Project.objects.filter(author=user)
        contributed_projects = Project.objects.filter(contributor__user=user)
        return authored_projects.union(contributed_projects).distinct()
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['get', 'post'])
    def contributors(self, request, pk=None):
        """Gérer les contributeurs d'un projet"""
        project = self.get_object()
        
        if request.method == 'GET':
            contributors = Contributor.objects.filter(project=project)
            serializer = ContributorSerializer(contributors, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Vérifier que l'utilisateur est l'auteur du projet
            if project.author != request.user:
                return Response(
                    {"error": "Seul l'auteur peut ajouter des contributeurs"}, 
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
                        {"error": "Cet utilisateur est déjà contributeur"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except User.DoesNotExist:
                return Response(
                    {"error": "Utilisateur non trouvé"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
    
    @action(detail=True, methods=['get', 'post'])
    def issues(self, request, pk=None):
        """Gérer les issues d'un projet"""
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
    """ViewSet pour gérer les contributeurs"""
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        if project_id:
            return Contributor.objects.filter(project_id=project_id)
        return Contributor.objects.none()


# Issue ViewSet
class IssueViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les issues"""
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        if project_id:
            return Issue.objects.filter(project_id=project_id)
        return Issue.objects.none()
    
    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        project = get_object_or_404(Project, id=project_id)
        serializer.save(author=self.request.user, project=project)
    
    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None, project_pk=None):
        """Gérer les commentaires d'une issue"""
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
    """ViewSet pour gérer les commentaires"""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        issue_id = self.kwargs.get('issue_pk')
        if issue_id:
            return Comment.objects.filter(issue_id=issue_id)
        return Comment.objects.none()
    
    def perform_create(self, serializer):
        issue_id = self.kwargs.get('issue_pk')
        issue = get_object_or_404(Issue, id=issue_id)
        serializer.save(author=self.request.user, issue=issue)
