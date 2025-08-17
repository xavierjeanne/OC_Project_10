from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Contributor


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
            raise serializers.ValidationError("Minimum age required is 15 years for GDPR compliance reasons.")
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


class ContributorSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    project = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Contributor
        fields = ['id', 'user', 'project', 'role']
        read_only_fields = ['role']  # Role is set automatically
