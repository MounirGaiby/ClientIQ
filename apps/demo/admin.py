from django.contrib import admin

from django.contrib import admin
from django.utils.html import format_html
from .models import DemoRequest


@admin.register(DemoRequest)
class DemoRequestAdmin(admin.ModelAdmin):
    """
    Admin interface for managing demo requests.
    """
    list_display = [
        'company_name',
        'full_name',
        'email',
        'company_size',
        'status_badge',
        'created_at',
        'actions_column'
    ]
    
    list_filter = [
        'status',
        'company_size',
        'industry',
        'created_at',
    ]
    
    search_fields = [
        'company_name',
        'contact_name',
        'contact_email',
        'industry',
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'company_size', 'industry')
        }),
        ('Contact Information', {
            'fields': ('contact_name', 'contact_email', 'contact_phone')
        }),
        ('Request Details', {
            'fields': ('message', 'status', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_requests', 'reject_requests', 'convert_to_tenant']
    
    def status_badge(self, obj):
        """Display status with color coding."""
        colors = {
            'pending': '#ffc107',
            'approved': '#28a745',
            'converted': '#007bff',
            'rejected': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def full_name(self, obj):
        """Display full name of the contact person."""
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Contact Name'
    
    def actions_column(self, obj):
        """Display action buttons."""
        if obj.status == 'approved':
            return format_html(
                '<a class="button" href="#" onclick="convertToTenant({})">Convert to Tenant</a>',
                obj.pk
            )
        return '-'
    actions_column.short_description = 'Actions'
    
    def approve_requests(self, request, queryset):
        """Bulk action to approve selected requests."""
        updated = queryset.update(status='approved')
        self.message_user(
            request,
            f'{updated} demo request(s) approved successfully.'
        )
    approve_requests.short_description = "Mark selected requests as approved"
    
    def reject_requests(self, request, queryset):
        """Bulk action to reject selected requests."""
        updated = queryset.update(status='rejected')
        self.message_user(
            request,
            f'{updated} demo request(s) rejected.'
        )
    reject_requests.short_description = "Mark selected requests as rejected"
    
    def convert_to_tenant(self, request, queryset):
        """Bulk action to convert approved requests to tenants."""
        # This will be implemented in Phase 2
        self.message_user(
            request,
            "Tenant conversion feature will be implemented in next phase."
        )
    convert_to_tenant.short_description = "Convert approved requests to tenants"
