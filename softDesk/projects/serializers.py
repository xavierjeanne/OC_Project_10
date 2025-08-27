from rest_framework import serializers
from django.conf import settings
from .models import Project, Issue, Comment


class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    contributor_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'type', 'author', 'created_time', 'contributor_count']
        read_only_fields = ['author', 'created_time', 'contributor_count']
        
    def get_contributor_count(self, obj):
        """
        Return the number of contributors instead of loading all contributors data
        This helps avoid N+1 queries when showing contributor counts
        """
        return obj.contributors.count()


class IssueSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    assignee_username = serializers.CharField(source='assignee.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Import here to avoid circular imports
        from accounts.models import User, Contributor
        
        # Instead of limiting the queryset, we'll do the validation in validate()
        # This allows us to provide clearer error messages
        self.fields['assignee'] = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all(),
            required=False, 
            allow_null=True,
            error_messages={
                'does_not_exist': "The specified user does not exist.",
                'invalid': "The provided user ID is not valid."
            }
        )
        
        # Store project ID for later validation if available
        if self.context.get('view'):
            view = self.context['view']
            self.project_id = view.kwargs.get('project_pk')
        else:
            self.project_id = None
    
    def validate(self, data):
        # Check that the assignee is a contributor to the project
        assignee = data.get('assignee')
        project = data.get('project') or (self.instance.project if self.instance else None)
        
        # If we're in the context of a nested view, get the project from the view
        if not project and self.context.get('view'):
            view = self.context['view']
            project_id = view.kwargs.get('project_pk')
            if project_id:
                try:
                    project = Project.objects.get(id=project_id)
                except Project.DoesNotExist:
                    raise serializers.ValidationError({
                        'project': f"Project with ID {project_id} does not exist."
                    })
        
        if assignee and project:
            from accounts.models import Contributor
            # Explicitly check if the user exists
            from accounts.models import User
            if not User.objects.filter(id=assignee.id).exists():
                raise serializers.ValidationError({
                    'assignee': f"User with ID {assignee.id} does not exist."
                })
            
            # Check if the user is a contributor to the project
            if not Contributor.objects.filter(project=project, user=assignee).exists():
                raise serializers.ValidationError({
                    'assignee': f"User {assignee.username} (ID: {assignee.id}) is not a contributor to project '{project.name}'."
                })
        
        return data
    
    class Meta:
        model = Issue
        fields = ['id', 'title', 'description', 'tag', 'priority', 'status', 
                 'project', 'project_name', 'author', 'assignee', 'assignee_username', 'created_time']
        read_only_fields = ['author', 'created_time', 'project', 'project_name', 'assignee_username']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    issue_title = serializers.CharField(source='issue.title', read_only=True)
    project_name = serializers.CharField(source='issue.project.name', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'description', 'issue', 'issue_title', 'project_name', 'author', 'created_time']
        read_only_fields = ['author', 'created_time', 'issue', 'issue_title', 'project_name']
