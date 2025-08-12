from django.contrib.auth.models import AbstractUser,Group,Permission
from django.db import models
import uuid

# -------------------
# Custom User Model
# -------------------
class User(AbstractUser):
    age = models.PositiveIntegerField(default=18)
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username

# -------------------
# Project Model
# -------------------
class Project(models.Model):
    BACK_END = 'BACK_END'
    FRONT_END = 'FRONT_END'
    IOS = 'IOS'
    ANDROID = 'ANDROID'

    PROJECT_TYPES = [
        (BACK_END, 'Back-end'),
        (FRONT_END, 'Front-end'),
        (IOS, 'iOS'),
        (ANDROID, 'Android')
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=PROJECT_TYPES)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_projects')
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# -------------------
# Contributor Model
# -------------------
class Contributor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f"{self.user.username} → {self.project.name}"

# -------------------
# Issue Model
# -------------------
class Issue(models.Model):
    TAG_CHOICES = [
        ('BUG', 'Bug'),
        ('FEATURE', 'Feature'),
        ('TASK', 'Task')
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High')
    ]

    STATUS_CHOICES = [
        ('TO_DO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('FINISHED', 'Finished')
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    tag = models.CharField(max_length=20, choices=TAG_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TO_DO')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_issues')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_issues')
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# -------------------
# Comment Model
# -------------------
class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField()
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.issue.title}"

