"""
Admin configuration for Permissions app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Permission, Role


@admin.register(Permission)
class CustomPermissionAdmin(admin.ModelAdmin):
    """Admin interface for custom permissions"""
    list_display = ['name', 'description', 'category', 'status_badge', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'category']
    ordering = ['category', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Permission Details', {
            'fields': ('name', 'description', 'category'),
            'description': 'Basic permission information'
        }),
        ('Status', {
            'fields': ('is_active',),
            'description': 'Permission availability status'
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Creation and modification timestamps'
        }),
    )
    
    def status_badge(self, obj):
        """Visual status indicator"""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Active</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Inactive</span>'
            )
    status_badge.short_description = 'Status'


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin interface for roles"""
    list_display = ['name', 'description', 'permissions_count', 'status_badge', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['permissions']
    
    fieldsets = (
        ('Role Information', {
            'fields': ('name', 'description'),
            'description': 'Basic role information'
        }),
        ('Permissions', {
            'fields': ('permissions',),
            'description': 'Select permissions for this role'
        }),
        ('Status', {
            'fields': ('is_active',),
            'description': 'Role availability status'
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Creation and modification timestamps'
        }),
    )
    
    def permissions_count(self, obj):
        """Count of permissions assigned to this role"""
        return obj.permissions.count()
    permissions_count.short_description = 'Permissions'
    
    def status_badge(self, obj):
        """Visual status indicator"""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Active</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Inactive</span>'
            )
    status_badge.short_description = 'Status'
