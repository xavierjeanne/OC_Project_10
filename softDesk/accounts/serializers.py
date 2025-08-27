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
            'password': {'write_only': True},
            'username': {'required': False},  # For updates
            'email': {'required': False},  # For updates
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required only for creation
        if self.instance is None:  # Creation
            self.fields['password'].required = True
            self.fields['username'].required = True
        else:  # Update - all fields are optional
            self.fields['password'].required = False
            self.fields['username'].required = False
            # Make all other fields optional for updates
            for field_name in self.fields:
                if field_name not in ['id']:
                    self.fields[field_name].required = False
    
    def validate_age(self, value):
        if value is not None and value < 15:
            raise serializers.ValidationError("Minimum age required is 15 years for GDPR compliance reasons.")
        return value
    
    def validate_can_be_contacted(self, value):
        if value and (self.instance is None or self.instance.age is None or self.instance.age < 15):
            # Check if a valid age has been provided in submitted data
            age_in_data = self.initial_data.get('age')
            if age_in_data is None or int(age_in_data) < 15:
                raise serializers.ValidationError("User must be at least 15 years old to consent to being contacted (GDPR compliance).")
        return value
    
    def validate_can_data_be_shared(self, value):
        if value and (self.instance is None or self.instance.age is None or self.instance.age < 15):
            # Check if a valid age has been provided in submitted data
            age_in_data = self.initial_data.get('age')
            if age_in_data is None or int(age_in_data) < 15:
                raise serializers.ValidationError("User must be at least 15 years old to consent to data sharing (GDPR compliance).")
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
    
    def validate(self, data):
        """Global validation to check GDPR data consistency"""
        # Check if the user is a minor
        age = data.get('age', None)
        
        # If age is provided and is less than 15 years
        if age is not None and age < 15:
            # Check that we are not trying to set can_be_contacted or can_data_be_shared to True
            if data.get('can_be_contacted', False):
                raise serializers.ValidationError({
                    'can_be_contacted': "Users under 15 years old cannot consent to being contacted (GDPR compliance)."
                })
            if data.get('can_data_be_shared', False):
                raise serializers.ValidationError({
                    'can_data_be_shared': "Users under 15 years old cannot consent to data sharing (GDPR compliance)."
                })
        
        # For updates, also check with existing age if not provided
        elif self.instance and age is None and self.instance.age is not None and self.instance.age < 15:
            # Check that we are not trying to set can_be_contacted or can_data_be_shared to True
            if data.get('can_be_contacted', False):
                raise serializers.ValidationError({
                    'can_be_contacted': "Users under 15 years old cannot consent to being contacted (GDPR compliance)."
                })
            if data.get('can_data_be_shared', False):
                raise serializers.ValidationError({
                    'can_data_be_shared': "Users under 15 years old cannot consent to data sharing (GDPR compliance)."
                })
        
        return data
    
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
    user_id = serializers.IntegerField(required=True)  # No longer write_only
    username = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Contributor
        fields = ['id', 'user', 'username', 'project', 'role', 'user_id']
        read_only_fields = ['role', 'user', 'project', 'username']  # These fields are set automatically
        
    def get_username(self, obj):
        return obj.user.username if obj.user else None
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Add notes about the fields to help users understand
        representation['notes'] = {
            "contributor_id": "Use this 'id' value when removing a contributor",
            "user_id": "Use this 'user_id' value when assigning issues to this contributor"
        }
        return representation
