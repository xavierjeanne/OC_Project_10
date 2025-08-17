from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import auth_views

app_name = 'accounts'

# Router for main endpoints
router = DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # JWT Authentication URLs
    path('auth/login/', auth_views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', auth_views.register_view, name='register'),
    path('auth/logout/', auth_views.logout_view, name='logout'),
    
    # URLs for contributors (nested under projects)
    path('projects/<int:project_pk>/users/', 
         views.ContributorViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='project-contributors-list'),
    path('projects/<int:project_pk>/users/<int:pk>/', 
         views.ContributorViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), 
         name='project-contributors-detail'),
]
