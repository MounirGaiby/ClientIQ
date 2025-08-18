from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.tenant_permissions.models import TenantRole

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data (read operations).
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'user_type', 'phone_number', 'is_active', 'roles',
            'department', 'job_title', 'is_tenant_admin',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_roles(self, obj):
        """Get user's roles within the tenant."""
        from apps.tenant_permissions.models import TenantUserRole
        user_roles = TenantUserRole.objects.filter(
            user=obj, 
            is_active=True,
            role__is_active=True
        ).select_related('role', 'role__role_group')
        
        return [
            {
                'id': ur.role.id,
                'name': ur.role.name,
                'role_group': ur.role.role_group.name
            }
            for ur in user_roles
        ]


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
            'phone_number', 'department', 'job_title', 
            'is_tenant_admin', 'password', 'role_ids'
        ]
    
    def create(self, validated_data):
        role_ids = validated_data.pop('role_ids', [])
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Assign roles
        if role_ids:
            from apps.tenant_permissions.models import TenantRole, TenantUserRole
            roles = TenantRole.objects.filter(id__in=role_ids, is_active=True)
            for role in roles:
                TenantUserRole.objects.create(
                    user=user,
                    role=role,
                    assigned_by=self.context['request'].user if 'request' in self.context else None
                )
        
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
            'phone_number', 'is_active', 'department', 
            'job_title', 'is_tenant_admin', 'role_ids'
        ]
    
    def update(self, instance, validated_data):
        role_ids = validated_data.pop('role_ids', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update roles if provided
        if role_ids is not None:
            from apps.tenant_permissions.models import TenantRole, TenantUserRole
            
            # Clear existing roles
            TenantUserRole.objects.filter(user=instance).update(is_active=False)
            
            # Add new roles
            roles = TenantRole.objects.filter(id__in=role_ids, is_active=True)
            for role in roles:
                TenantUserRole.objects.update_or_create(
                    user=instance,
                    role=role,
                    defaults={
                        'is_active': True,
                        'assigned_by': self.context['request'].user if 'request' in self.context else None
                    }
                )
        
        return instance
