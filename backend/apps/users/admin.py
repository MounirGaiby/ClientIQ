from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.utils.html import format_html
from django.db import models
from .models import CustomUser


class GroupInline(admin.TabularInline):
    """Inline display of user groups"""
    model = CustomUser.groups.through
    extra = 0
    verbose_name = "Group Membership"
    verbose_name_plural = "Group Memberships"


class UserPermissionInline(admin.TabularInline):
    """Inline display of individual user permissions"""
    model = CustomUser.user_permissions.through
    extra = 0
    verbose_name = "Individual Permission"
    verbose_name_plural = "Individual Permissions"


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Comprehensive admin interface for tenant users"""
    list_display = [
        'email', 'full_name_display', 'is_admin_badge', 'status_badge', 
        'group_count', 'permission_count', 'last_login_display', 'date_joined'
    ]
    list_filter = ['is_active', 'is_admin', 'date_joined', 'groups']
    search_fields = ['email', 'first_name', 'last_name', 'job_title', 'department']
    readonly_fields = ['date_joined', 'last_login', 'password']
    filter_horizontal = ['groups', 'user_permissions']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('User Information', {
            'fields': ('email', 'first_name', 'last_name'),
            'description': 'Basic user information'
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'job_title', 'department'),
            'classes': ('collapse',),
            'description': 'Additional contact and role information'
        }),
        ('Permissions & Access', {
            'fields': ('is_active', 'is_admin'),
            'description': 'is_admin: User has all permissions within this tenant (not Django admin access)'
        }),
        ('Group Memberships', {
            'fields': ('groups',),
            'description': 'Groups provide role-based permissions'
        }),
        ('Individual Permissions', {
            'fields': ('user_permissions',),
            'classes': ('collapse',),
            'description': 'Specific permissions assigned directly to this user'
        }),
        ('Password', {
            'fields': ('password',),
            'classes': ('collapse',),
            'description': 'Encrypted password hash'
        }),
        ('Login History', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',),
            'description': 'Account creation and last login timestamps'
        }),
    )
    
    actions = ['activate_users', 'deactivate_users', 'make_admin', 'remove_admin']
    
    def full_name_display(self, obj):
        """Display full name with fallback to email"""
        return obj.get_full_name() or obj.email
    full_name_display.short_description = 'Full Name'
    full_name_display.admin_order_field = 'first_name'
    
    def is_admin_badge(self, obj):
        """Visual admin status indicator"""
        if obj.is_admin:
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">ADMIN</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">USER</span>'
        )
    is_admin_badge.short_description = 'Role'
    is_admin_badge.admin_order_field = 'is_admin'
    
    def status_badge(self, obj):
        """Visual status indicator"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">ACTIVE</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">INACTIVE</span>'
            )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'is_active'
    
    def group_count(self, obj):
        """Count of groups user belongs to"""
        return obj.groups.count()
    group_count.short_description = 'Groups'
    
    def permission_count(self, obj):
        """Count of individual permissions"""
        return obj.user_permissions.count()
    permission_count.short_description = 'Individual Permissions'
    
    def last_login_display(self, obj):
        """Format last login date"""
        if obj.last_login:
            return obj.last_login.strftime('%Y-%m-%d %H:%M')
        return 'Never'
    last_login_display.short_description = 'Last Login'
    last_login_display.admin_order_field = 'last_login'
    
    def activate_users(self, request, queryset):
        """Bulk activate users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Successfully activated {updated} user(s).')
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        """Bulk deactivate users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Successfully deactivated {updated} user(s).')
    deactivate_users.short_description = 'Deactivate selected users'
    
    def make_admin(self, request, queryset):
        """Bulk make users admin"""
        updated = queryset.update(is_admin=True)
        self.message_user(request, f'Successfully made {updated} user(s) admin.')
    make_admin.short_description = 'Make selected users admin'
    
    def remove_admin(self, request, queryset):
        """Bulk remove admin privileges"""
        updated = queryset.update(is_admin=False)
        self.message_user(request, f'Successfully removed admin privileges from {updated} user(s).')
    remove_admin.short_description = 'Remove admin privileges from selected users'
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).prefetch_related('groups', 'user_permissions')

