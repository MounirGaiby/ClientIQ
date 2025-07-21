from django.contrib import admin
from django.utils.html import format_html
from .models import Tenant, Domain


class DomainInline(admin.TabularInline):
    """Inline admin for tenant domains."""
    model = Domain
    extra = 1
    fields = ['domain', 'is_primary']


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """
    Admin interface for managing tenants.
    """
    list_display = [
        'name',
        'schema_name',
        'subscription_status_badge',
        'created_on',
        'is_active',
        'domain_count',
        'actions_column'
    ]
    
    list_filter = [
        'subscription_status',
        'is_active',
        'created_on',
    ]
    
    search_fields = [
        'name',
        'schema_name',
        'contact_email',
    ]
    
    readonly_fields = ['schema_name', 'created_on']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'schema_name', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone')
        }),
        ('Subscription', {
            'fields': ('subscription_status',)
        }),
        ('Timestamps', {
            'fields': ('created_on',),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [DomainInline]
    
    actions = ['activate_tenants', 'suspend_tenants', 'create_admin_user']
    
    def subscription_status_badge(self, obj):
        """Display subscription status with color coding."""
        colors = {
            'trial': '#ffc107',
            'active': '#28a745',
            'suspended': '#dc3545',
            'cancelled': '#6c757d',
        }
        color = colors.get(obj.subscription_status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_subscription_status_display()
        )
    subscription_status_badge.short_description = 'Subscription'
    
    def domain_count(self, obj):
        """Display number of domains for this tenant."""
        count = obj.domains.count()
        return f"{count} domain{'s' if count != 1 else ''}"
    domain_count.short_description = 'Domains'
    
    def actions_column(self, obj):
        """Display action buttons."""
        return format_html(
            '<a class="button" href="#" onclick="createAdminUser({})">Create Admin User</a>',
            obj.pk
        )
    actions_column.short_description = 'Actions'
    
    def activate_tenants(self, request, queryset):
        """Bulk action to activate selected tenants."""
        updated = queryset.update(is_active=True, subscription_status='active')
        self.message_user(
            request,
            f'{updated} tenant(s) activated successfully.'
        )
    activate_tenants.short_description = "Activate selected tenants"
    
    def suspend_tenants(self, request, queryset):
        """Bulk action to suspend selected tenants."""
        updated = queryset.update(subscription_status='suspended')
        self.message_user(
            request,
            f'{updated} tenant(s) suspended.'
        )
    suspend_tenants.short_description = "Suspend selected tenants"
    
    def create_admin_user(self, request, queryset):
        """Bulk action to create admin users for tenants."""
        # This will be implemented in Phase 4
        self.message_user(
            request,
            "Admin user creation feature will be implemented in Phase 4."
        )
    create_admin_user.short_description = "Create admin users for selected tenants"


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    """
    Admin interface for managing domains.
    """
    list_display = ['domain', 'tenant', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['domain', 'tenant__name']
