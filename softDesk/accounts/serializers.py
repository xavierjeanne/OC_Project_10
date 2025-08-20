from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Contributor


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'age', 
                 'can_be_contacted', 'can_data_be_shared', 'password']
        extra_kwargs = {
            'password': {'write_only': True} 
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make password required only for creation
        if self.instance is None:  # Creation
            self.fields['password'].required = True
        else:  # Update
            self.fields['password'].required = False
    
    def validate_age(self, value):
        if value is not None and value < 15:
            raise serializers.ValidationError("Minimum age required is 15 years for GDPR compliance reasons.")
        return value
    
    def validate_password(self, value):
        if value:  # Only validate if password is provided
            validate_password(value)
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update password only if provided
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class ContributorSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    project = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Contributor
        fields = ['id', 'user', 'project', 'role']
        read_only_fields = ['role']  # Role is set automatically
