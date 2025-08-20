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
        from accounts.models import User, Contributor
        
        # Si nous avons le contexte de la vue, limiter les assignee aux contributeurs du projet
        if self.context.get('view'):
            view = self.context['view']
            project_id = view.kwargs.get('project_pk')
            if project_id:
                # Limiter les choix d'assignee aux contributeurs du projet
                contributor_users = User.objects.filter(
                    contributions__project_id=project_id
                )
                self.fields['assignee'] = serializers.PrimaryKeyRelatedField(
                    queryset=contributor_users,
                    required=False, 
                    allow_null=True
                )
            else:
                self.fields['assignee'] = serializers.PrimaryKeyRelatedField(
                    queryset=User.objects.all(),
                    required=False, 
                    allow_null=True
                )
        else:
            self.fields['assignee'] = serializers.PrimaryKeyRelatedField(
                queryset=User.objects.all(),
                required=False, 
                allow_null=True
            )
    
    def validate(self, data):
        # Vérifier que l'assignee est contributeur du projet
        assignee = data.get('assignee')
        project = data.get('project') or (self.instance.project if self.instance else None)
        
        # Si nous sommes dans le contexte d'une vue imbriquée, récupérer le projet depuis la vue
        if not project and self.context.get('view'):
            view = self.context['view']
            project_id = view.kwargs.get('project_pk')
            if project_id:
                project = Project.objects.get(id=project_id)
        
        if assignee and project:
            from accounts.models import Contributor
            if not Contributor.objects.filter(project=project, user=assignee).exists():
                raise serializers.ValidationError({
                    'assignee': 'L\'utilisateur assigné doit être contributeur du projet.'
                })
        
        return data
    
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
