from rest_framework import serializers
from django.conf import settings
from .models import Project, Issue, Comment


class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'type', 'author', 'created_time']
        read_only_fields = ['author', 'created_time']


class IssueSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Import here to avoid circular imports
        from accounts.models import User
        self.fields['assignee'] = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all(),
            required=False, 
            allow_null=True
        )
    
    class Meta:
        model = Issue
        fields = ['id', 'title', 'description', 'tag', 'priority', 'status', 
                 'project', 'author', 'assignee', 'created_time']
        read_only_fields = ['author', 'created_time', 'project']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'description', 'issue', 'author', 'created_time']
        read_only_fields = ['author', 'created_time', 'issue']
