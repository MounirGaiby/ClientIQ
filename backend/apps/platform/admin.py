from django.contrib import admin
from .models import SuperUser


@admin.register(SuperUser)
class SuperUserAdmin(admin.ModelAdmin):
    """Admin interface for platform super users"""
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'is_readonly', 'date_joined']
    list_filter = ['is_active', 'is_readonly', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login']
    
    fieldsets = (
        ('User Info', {
            'fields': ('email', 'first_name', 'last_name')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_readonly'),
            'description': 'is_readonly: Can only view Django admin, cannot edit/delete'
        }),
        ('Dates', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )
