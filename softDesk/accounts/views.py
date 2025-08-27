from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import User, Contributor
from .serializers import UserSerializer, ContributorSerializer
from .permissions import IsOwnerOrReadOnly, IsProjectAuthorForContributors


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for managing users"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        # Users can see all other users (for assignment)
        # but can only modify their own profile (managed by IsOwnerOrReadOnly)
        return User.objects.all()


class ContributorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing contributors"""
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, IsProjectAuthorForContributors]
    
    def get_queryset(self):
        # Use select_related to prefetch related user and project
        base_queryset = self.queryset.select_related('user', 'project')
        
        # Filter by project if project_pk is provided
        project_id = self.kwargs.get('project_pk')
        if project_id:
            return base_queryset.filter(project_id=project_id)
        
        # Otherwise, return contributors from projects where the user is author or contributor
        user = self.request.user
        from projects.models import Project
        user_projects = Project.objects.filter(
            Q(author=user) | Q(contributors__user=user)
        ).distinct()
        return base_queryset.filter(project__in=user_projects)
    
    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        # Import here to avoid circular imports
        from projects.models import Project
        project = get_object_or_404(Project, id=project_id)
        
        # Explicit verification that the user is the project author
        if project.author != self.request.user:
            raise ValidationError({"detail": "Only the project author can add contributors."})
        
        # user_id is now validated by the serializer
        user_id = serializer.validated_data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
        # Check that the user is not already a contributor
        if Contributor.objects.filter(user=user, project=project).exists():
            raise ValidationError({"detail": "This user is already a contributor to this project."})
            
        # Create the contributor
        serializer.save(project=project, user=user, role='CONTRIBUTOR')
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Prevent deletion of the project author (who is also a contributor)
        if instance.role == 'AUTHOR':
            raise ValidationError({"detail": "Cannot remove the project author."})
            
        # Additional check that the user is the project author
        if instance.project.author != request.user:
            raise ValidationError({"detail": "Only the project author can remove contributors."})
            
        # Make sure we're not removing the last contributor
        if instance.project.contributors.count() <= 1:
            raise ValidationError({"detail": "Cannot remove the last contributor from the project."})
            
        # Capture username for the response message
        username = instance.user.username
        project_name = instance.project.name
        
        # Delete the contributor
        instance.delete()
        
        # Return a success message
        return Response({
            "detail": f"Contributor '{username}' removed from project '{project_name}'"
        }, status=status.HTTP_200_OK)
