from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.permissions.models import Role

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data (read operations).
    """
    roles = serializers.StringRelatedField(many=True, read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'user_type', 'phone_number', 'is_active', 'roles',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for user creation.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'user_type',
            'phone_number', 'password', 'role_ids'
        ]
    
    def create(self, validated_data):
        role_ids = validated_data.pop('role_ids', [])
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Assign roles
        if role_ids:
            roles = Role.objects.filter(id__in=role_ids, is_active=True)
            for role in roles:
                role.users.add(user)
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for user updates.
    """
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'user_type',
            'phone_number', 'is_active', 'role_ids'
        ]
    
    def update(self, instance, validated_data):
        role_ids = validated_data.pop('role_ids', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update roles if provided
        if role_ids is not None:
            # Clear existing roles
            for role in instance.roles.all():
                role.users.remove(instance)
            
            # Add new roles
            roles = Role.objects.filter(id__in=role_ids, is_active=True)
            for role in roles:
                role.users.add(instance)
        
        return instance
