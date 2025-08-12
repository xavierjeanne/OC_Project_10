from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Project, Contributor, Issue, Comment


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'age', 
                 'can_be_contacted', 'can_data_be_shared', 'password']
        extra_kwargs = {
            'password': {'write_only': True} 
        }
    
    def validate_age(self, value):
        if value is not None and value < 15:
            raise serializers.ValidationError("L'âge minimum requis est de 15 ans pour des raisons de conformité RGPD.")
        return value
    
    def validate_password(self, value):
        validate_password(value)
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'type', 'author', 'created_time']
        read_only_fields = ['author', 'created_time']


class ContributorSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    project = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Contributor
        fields = ['id', 'user', 'project']


class IssueSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        required=False, 
        allow_null=True
    )
    
    class Meta:
        model = Issue
        fields = ['id', 'title', 'description', 'tag', 'priority', 'status', 
                 'project', 'author', 'assignee', 'created_time']
        read_only_fields = ['author', 'created_time']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'description', 'issue', 'author', 'created_time']
        read_only_fields = ['author', 'created_time']
