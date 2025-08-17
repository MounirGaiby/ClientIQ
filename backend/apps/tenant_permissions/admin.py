from django.contrib import admin

from django.contrib import admin
from django.utils.html import format_html
from .models import TenantRoleGroup, TenantRole, TenantUserRole


class TenantRoleInline(admin.TabularInline):
    """Inline admin for tenant roles."""
    model = TenantRole
    extra = 0
    fields = ['name', 'description', 'is_active']


@admin.register(TenantRoleGroup)
class TenantRoleGroupAdmin(admin.ModelAdmin):
    """
    Admin interface for managing tenant role groups.
    """
    list_display = [
        'name',
        'permission_count',
        'role_count',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'is_active',
        'created_at',
    ]
    
    search_fields = [
        'name',
        'description',
    ]
    
    readonly_fields = ['original_role_group_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Permissions', {
            'fields': ('permission_codenames',)
        }),
        ('Configuration', {
            'fields': ('is_active', 'original_role_group_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [TenantRoleInline]
    
    def permission_count(self, obj):
        """Display number of permissions in this role group."""
        count = len(obj.permission_codenames) if obj.permission_codenames else 0
        return f"{count} permission{'s' if count != 1 else ''}"
    permission_count.short_description = 'Permissions'
    
    def role_count(self, obj):
        """Display number of roles in this role group."""
        count = obj.roles.count()
        return f"{count} role{'s' if count != 1 else ''}"
    role_count.short_description = 'Roles'


@admin.register(TenantRole)
class TenantRoleAdmin(admin.ModelAdmin):
    """
    Admin interface for managing tenant roles.
    """
    list_display = [
        'name',
        'role_group',
        'user_count',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'role_group',
        'is_active',
        'created_at',
    ]
    
    search_fields = [
        'name',
        'description',
        'role_group__name',
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'role_group', 'description')
        }),
        ('Configuration', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_count(self, obj):
        """Display number of users assigned to this role."""
        count = obj.user_assignments.filter(is_active=True).count()
        return f"{count} user{'s' if count != 1 else ''}"
    user_count.short_description = 'Users'


@admin.register(TenantUserRole)
class TenantUserRoleAdmin(admin.ModelAdmin):
    """
    Admin interface for managing tenant user role assignments.
    """
    list_display = [
        'user',
        'role',
        'role_group_name',
        'assigned_by',
        'is_active',
        'assigned_at'
    ]
    
    list_filter = [
        'role__role_group',
        'role',
        'is_active',
        'assigned_at',
    ]
    
    search_fields = [
        'user__first_name',
        'user__last_name',
        'user__email',
        'role__name',
        'role__role_group__name',
    ]
    
    readonly_fields = ['assigned_at']
    
    fieldsets = (
        ('Assignment', {
            'fields': ('user', 'role', 'assigned_by')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('assigned_at',),
            'classes': ('collapse',)
        }),
    )
    
    def role_group_name(self, obj):
        """Display role group name."""
        return obj.role.role_group.name
    role_group_name.short_description = 'Role Group'
