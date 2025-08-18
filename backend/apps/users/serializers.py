from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data (read operations).
    """
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    user_type = serializers.CharField(source='profile.user_type', read_only=True)
    phone_number = serializers.CharField(source='profile.phone_number', read_only=True)
    department = serializers.CharField(source='profile.department', read_only=True)
    job_title = serializers.CharField(source='profile.job_title', read_only=True)
    is_tenant_admin = serializers.BooleanField(source='profile.is_tenant_admin', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'user_type', 'phone_number', 'is_active', 
            'department', 'job_title', 'is_tenant_admin',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for user creation.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    user_type = serializers.CharField(write_only=True, required=False)
    phone_number = serializers.CharField(write_only=True, required=False)
    department = serializers.CharField(write_only=True, required=False)
    job_title = serializers.CharField(write_only=True, required=False)
    is_tenant_admin = serializers.BooleanField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'password',
            'user_type', 'phone_number', 'department', 
            'job_title', 'is_tenant_admin'
        ]
    
    def create(self, validated_data):
        # Extract profile data
        profile_data = {
            'user_type': validated_data.pop('user_type', 'user'),
            'phone_number': validated_data.pop('phone_number', ''),
            'department': validated_data.pop('department', ''),
            'job_title': validated_data.pop('job_title', ''),
            'is_tenant_admin': validated_data.pop('is_tenant_admin', False),
        }
        
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Update the auto-created profile
        for key, value in profile_data.items():
            setattr(user.profile, key, value)
        user.profile.save()
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for user updates.
    """
    user_type = serializers.CharField(write_only=True, required=False)
    phone_number = serializers.CharField(write_only=True, required=False)
    department = serializers.CharField(write_only=True, required=False)
    job_title = serializers.CharField(write_only=True, required=False)
    is_tenant_admin = serializers.BooleanField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'is_active',
            'user_type', 'phone_number', 'department', 
            'job_title', 'is_tenant_admin'
        ]
    
    def update(self, instance, validated_data):
        # Extract profile data
        profile_data = {}
        for field in ['user_type', 'phone_number', 'department', 'job_title', 'is_tenant_admin']:
            if field in validated_data:
                profile_data[field] = validated_data.pop(field)
        
        # Update user instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile
        if profile_data:
            for key, value in profile_data.items():
                setattr(instance.profile, key, value)
            instance.profile.save()
        
        return instance
