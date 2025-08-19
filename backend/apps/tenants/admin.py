from django.contrib import admin
from apps.tenants.models import Tenant, Domain


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'schema_name', 'plan', 'is_active', 'created_at']
    list_filter = ['plan', 'is_active', 'industry', 'company_size']
    search_fields = ['name', 'schema_name', 'contact_email']
    readonly_fields = ['schema_name', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'schema_name')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'billing_email')
        }),
        ('Business Information', {
            'fields': ('industry', 'company_size')
        }),
        ('Subscription', {
            'fields': ('plan', 'is_active')
        }),
        ('Settings', {
            'fields': ('settings',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'tenant', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['domain', 'tenant__name']
