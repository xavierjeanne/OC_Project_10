from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
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
        # Les utilisateurs peuvent voir tous les autres utilisateurs (pour assignation)
        # mais ne peuvent modifier que leur propre profil (géré par IsOwnerOrReadOnly)
        return User.objects.all()


class ContributorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing contributors"""
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, IsProjectAuthorForContributors]
    
    def get_queryset(self):
        # Filtre par projet si project_pk est fourni
        project_id = self.kwargs.get('project_pk')
        if project_id:
            return self.queryset.filter(project_id=project_id)
        
        # Sinon, retourne les contributeurs des projets où l'utilisateur est auteur ou contributeur
        user = self.request.user
        from projects.models import Project
        user_projects = Project.objects.filter(
            Q(author=user) | Q(contributors__user=user)
        ).distinct()
        return self.queryset.filter(project__in=user_projects)
    
    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        # Import here to avoid circular imports
        from projects.models import Project
        project = get_object_or_404(Project, id=project_id)
        
        # Vérifier que l'utilisateur est l'auteur du projet
        if project.author != self.request.user:
            raise ValidationError({"detail": "Seul l'auteur du projet peut ajouter des contributeurs."})
        
        # Get user_id from request data
        user_id = self.request.data.get('user_id')
        if not user_id:
            raise ValidationError({"user_id": "This field is required."})
        
        user = get_object_or_404(User, id=user_id)
        
        # Vérifier que l'utilisateur n'est pas déjà contributeur
        if Contributor.objects.filter(project=project, user=user).exists():
            raise ValidationError({"detail": "Cet utilisateur est déjà contributeur de ce projet."})
        
        serializer.save(project=project, user=user, role='CONTRIBUTOR')
