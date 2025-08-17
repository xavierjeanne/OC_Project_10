from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import User, Contributor
from .serializers import UserSerializer, ContributorSerializer


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


class ContributorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing contributors"""
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Override to filter by project
        project_id = self.kwargs.get('project_pk')
        if project_id:
            return self.queryset.filter(project_id=project_id)
        return self.queryset.none()
    
    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        # Import here to avoid circular imports
        from projects.models import Project
        project = get_object_or_404(Project, id=project_id)
        
        # Get user_id from request data
        user_id = self.request.data.get('user_id')
        if not user_id:
            raise ValidationError({"user_id": "This field is required."})
        
        user = get_object_or_404(User, id=user_id)
        serializer.save(project=project, user=user)
