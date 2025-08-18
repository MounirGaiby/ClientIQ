from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data (read operations).
    """
    full_name = serializers.CharField(read_only=True)
    
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
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'password',
            'user_type', 'phone_number', 'department', 
            'job_title', 'is_tenant_admin'
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for user updates.
    """
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'is_active',
            'user_type', 'phone_number', 'department', 
            'job_title', 'is_tenant_admin'
        ]
