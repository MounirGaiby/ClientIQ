from rest_framework import serializers
from .models import Role, RoleGroup, Permission


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for permissions (read-only).
    """
    class Meta:
        model = Permission
        fields = [
            'id', 'codename', 'name', 'description', 'module',
            'resource', 'permission_type', 'is_system'
        ]


class RoleGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for role groups.
    """
    role_count = serializers.SerializerMethodField()
    
    class Meta:
        model = RoleGroup
        fields = [
            'id', 'name', 'description', 'is_active',
            'role_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_role_count(self, obj):
        return obj.roles.count()


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for roles.
    """
    role_group_name = serializers.CharField(source='role_group.name', read_only=True)
    permission_count = serializers.SerializerMethodField()
    user_count = serializers.SerializerMethodField()
    permissions = PermissionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'role_group', 'role_group_name',
            'permissions', 'is_active', 'is_system',
            'permission_count', 'user_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_system']
    
    def get_permission_count(self, obj):
        return obj.permissions.count()
    
    def get_user_count(self, obj):
        return obj.users.count()


class RoleCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for role creation.
    """
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Role
        fields = [
            'name', 'description', 'role_group', 'permission_ids'
        ]
    
    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        
        role = Role.objects.create(**validated_data)
        
        # Assign permissions
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)
        
        return role
