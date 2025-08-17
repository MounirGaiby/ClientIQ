from django.contrib import admin

from django.contrib import admin
from django.utils.html import format_html
from .models import Permission, RoleGroup, RoleGroupPermission


class RoleGroupPermissionInline(admin.TabularInline):
    """Inline admin for role group permissions."""
    model = RoleGroupPermission
    extra = 0
    fields = ['permission', 'granted_at']
    readonly_fields = ['granted_at']


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """
    Admin interface for managing permissions.
    """
    list_display = [
        'name',
        'codename',
        'category',
        'super_user_badge',
        'is_active',
        'usage_count',
        'created_at'
    ]
    
    list_filter = [
        'category',
        'is_super_user_only',
        'is_active',
        'created_at',
    ]
    
    search_fields = [
        'name',
        'codename',
        'description',
        'category',
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'codename', 'category')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Access Control', {
            'fields': ('is_super_user_only', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def super_user_badge(self, obj):
        """Display super user status with color coding."""
        if obj.is_super_user_only:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">Super User Only</span>'
            )
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">Tenant Users</span>'
        )
    super_user_badge.short_description = 'Access Level'
    
    def usage_count(self, obj):
        """Display how many role groups use this permission."""
        count = obj.group_permissions.count()
        return f"{count} role group{'s' if count != 1 else ''}"
    usage_count.short_description = 'Usage'


@admin.register(RoleGroup)
class RoleGroupAdmin(admin.ModelAdmin):
    """
    Admin interface for managing role groups.
    """
    list_display = [
        'name',
        'default_badge',
        'super_user_badge',
        'permission_count',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'is_default',
        'is_super_user_group',
        'is_active',
        'created_at',
    ]
    
    search_fields = [
        'name',
        'description',
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Configuration', {
            'fields': ('is_default', 'is_super_user_group', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [RoleGroupPermissionInline]
    
    def default_badge(self, obj):
        """Display default status with color coding."""
        if obj.is_default:
            return format_html(
                '<span style="color: #007bff; font-weight: bold;">Default</span>'
            )
        return '-'
    default_badge.short_description = 'Default'
    
    def super_user_badge(self, obj):
        """Display super user group status."""
        if obj.is_super_user_group:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">Super User Group</span>'
            )
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">Tenant Group</span>'
        )
    super_user_badge.short_description = 'Group Type'
    
    def permission_count(self, obj):
        """Display number of permissions in this role group."""
        count = obj.permissions.count()
        return f"{count} permission{'s' if count != 1 else ''}"
    permission_count.short_description = 'Permissions'


@admin.register(RoleGroupPermission)
class RoleGroupPermissionAdmin(admin.ModelAdmin):
    """
    Admin interface for role group permission relationships.
    """
    list_display = [
        'role_group',
        'permission',
        'permission_category',
        'granted_at'
    ]
    
    list_filter = [
        'role_group',
        'permission__category',
        'permission__is_super_user_only',
        'granted_at',
    ]
    
    search_fields = [
        'role_group__name',
        'permission__name',
        'permission__codename',
    ]
    
    readonly_fields = ['granted_at']
    
    def permission_category(self, obj):
        """Display permission category."""
        return obj.permission.category
    permission_category.short_description = 'Category'
