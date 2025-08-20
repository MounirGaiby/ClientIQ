from rest_framework import serializers
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data (read operations).
    """
    full_name = serializers.SerializerMethodField()
    
    def get_full_name(self, obj):
        """Return the full name of the user."""
        return f"{obj.first_name} {obj.last_name}".strip() if obj.first_name or obj.last_name else ""
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'is_active', 'department', 'job_title', 
            'is_admin', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'full_name']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for user creation.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = CustomUser
        fields = [
            'email', 'first_name', 'last_name', 'password',
            'phone_number', 'department', 'job_title', 'is_admin'
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for user updates.
    """
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'phone_number', 
            'department', 'job_title', 'is_admin'
        ]
