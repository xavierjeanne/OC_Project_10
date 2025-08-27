import uuid
from django.db import models
from django.conf import settings


class Project(models.Model):
    """Model for projects"""
    TYPE_CHOICES = [
        ('BACK_END', 'Back-end'),
        ('FRONT_END', 'Front-end'),
        ('IOS', 'iOS'),
        ('ANDROID', 'Android'),
    ]
    
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_projects')
    created_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_time']  # Most recent first
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Import here to avoid circular imports
            from accounts.models import Contributor
            Contributor.objects.get_or_create(
                user=self.author,
                project=self,
                defaults={'role': 'AUTHOR'}
            )
    
    def __str__(self):
        return self.name


class Issue(models.Model):
    """Model for issues"""
    TAG_CHOICES = [
        ('BUG', 'Bug'),
        ('FEATURE', 'Feature'),
        ('TASK', 'Task'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('TO_DO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('FINISHED', 'Finished'),
    ]
    
    title = models.CharField(max_length=128)
    description = models.TextField()
    tag = models.CharField(max_length=10, choices=TAG_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='TO_DO')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_issues')
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_issues')
    created_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_time']  # Most recent first
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    """Model for comments"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField()
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_comments')
    created_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_time']  # Oldest first (chronological order)
    
    def __str__(self):
        return f"Comment on {self.issue.title} by {self.author.username}"
