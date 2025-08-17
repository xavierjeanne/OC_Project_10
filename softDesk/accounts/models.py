from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with GDPR compliance"""
    age = models.PositiveIntegerField(null=True, blank=True)
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Contributor(models.Model):
    """Model to manage project contributors"""
    ROLE_CHOICES = [
        ('AUTHOR', 'Author'),
        ('CONTRIBUTOR', 'Contributor'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contributions')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='contributors')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CONTRIBUTOR')
    
    class Meta:
        unique_together = ['user', 'project']
    
    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.role})"
