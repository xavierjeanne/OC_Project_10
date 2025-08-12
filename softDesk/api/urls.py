from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

# Router principal
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'projects', views.ProjectViewSet, basename='project')

urlpatterns = [
    path('', include(router.urls)),
    
    # URLs pour les contributeurs
    path('projects/<int:project_pk>/users/', 
         views.ContributorViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='project-contributors-list'),
    path('projects/<int:project_pk>/users/<int:pk>/', 
         views.ContributorViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), 
         name='project-contributors-detail'),
    
    # URLs pour les issues
    path('projects/<int:project_pk>/issues/', 
         views.IssueViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='project-issues-list'),
    path('projects/<int:project_pk>/issues/<int:pk>/', 
         views.IssueViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), 
         name='project-issues-detail'),
    
    # URLs pour les commentaires
    path('projects/<int:project_pk>/issues/<int:issue_pk>/comments/', 
         views.CommentViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='issue-comments-list'),
    path('projects/<int:project_pk>/issues/<int:issue_pk>/comments/<str:pk>/', 
         views.CommentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), 
         name='issue-comments-detail'),
]
