from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Permission
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import SuperUser


@admin.register(SuperUser)
class SuperUserAdmin(admin.ModelAdmin):
    """Comprehensive admin interface for platform super users"""
    list_display = ['email', 'full_name_display', 'status_badge', 'last_login_display', 'date_joined']
    list_filter = ['is_active', 'date_joined', 'last_login']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login', 'password']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('User Information', {
            'fields': ('email', 'first_name', 'last_name'),
            'description': 'Basic user information for platform administration'
        }),
        ('Access Control', {
            'fields': ('is_active',),
            'description': 'All platform users have full admin access by default. Only deactivate if access should be revoked.'
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
    
    actions = ['activate_users', 'deactivate_users']
    
    def full_name_display(self, obj):
        """Display full name with fallback to email"""
        return obj.get_full_name() or obj.email
    full_name_display.short_description = 'Full Name'
    full_name_display.admin_order_field = 'first_name'
    
    def status_badge(self, obj):
        """Visual status indicator"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px;">ACTIVE</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px;">INACTIVE</span>'
            )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'is_active'
    
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
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related()


# Platform-wide admin customizations
admin.site.site_header = 'ClientIQ Platform Administration'
admin.site.site_title = 'ClientIQ Admin'
admin.site.index_title = 'Platform Management Dashboard'
admin.site.site_url = None  # Remove "View Site" link

# Customize admin index page
def get_app_list(self, request):
    """
    Return a sorted list of all the installed apps that have been
    registered in this site.
    """
    app_dict = self._build_app_dict(request)
    
    # Define custom ordering for apps
    app_order = [
        'platform',       # Platform SuperUsers first
        'tenants',        # Tenant management
        'demo',           # Demo requests  
        'users',          # Tenant users
        'contacts',       # Business data
        'permissions',    # Custom permissions & roles
        'authentication', # Auth & permissions
        'token_blacklist', # JWT token management
        'contenttypes',   # Django internals
        'admin',          # Admin logs
        'sessions',       # Sessions
    ]
    
    # Custom app display names
    app_names = {
        'platform': 'Platform Administration',
        'tenants': 'Tenant Management', 
        'demo': 'Demo Requests',
        'users': 'Tenant Users',
        'contacts': 'Business Contacts',
        'permissions': 'Permissions & Roles',
        'authentication': 'Authentication & Security',
        'token_blacklist': 'JWT Token Management',
        'contenttypes': 'Content Types',
        'admin': 'Admin Logs',
        'sessions': 'User Sessions',
    }
    
    # Sort apps according to our custom order
    app_list = []
    for app_name in app_order:
        if app_name in app_dict:
            app_dict[app_name]['name'] = app_names.get(app_name, app_dict[app_name]['name'])
            app_list.append(app_dict[app_name])
    
    # Add any remaining apps not in our order
    for app_name, app_data in app_dict.items():
        if app_name not in app_order:
            app_data['name'] = app_names.get(app_name, app_data['name'])
            app_list.append(app_data)
    
    return app_list

# Apply the custom app list method to admin site
admin.AdminSite.get_app_list = get_app_list


# Additional Django system model admin registrations

@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    """Admin interface for Django ContentTypes"""
    list_display = ['app_label', 'model', 'permission_count']
    list_filter = ['app_label']
    search_fields = ['app_label', 'model']
    ordering = ['app_label', 'model']
    readonly_fields = ['app_label', 'model']
    
    def permission_count(self, obj):
        return obj.permission_set.count()
    permission_count.short_description = 'Permissions'


@admin.register(Permission)
class SystemPermissionAdmin(admin.ModelAdmin):
    """Admin interface for Django System Permissions"""
    list_display = ['name', 'content_type', 'codename']
    list_filter = ['content_type']
    search_fields = ['name', 'codename', 'content_type__model']
    ordering = ['content_type', 'codename']
    readonly_fields = ['codename']


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    """Admin interface for Django Sessions"""
    list_display = ['session_key_short', 'expire_date', 'is_expired']
    list_filter = ['expire_date']
    search_fields = ['session_key']
    ordering = ['-expire_date']
    readonly_fields = ['session_key', 'session_data', 'expire_date']
    
    def session_key_short(self, obj):
        return f"{obj.session_key[:10]}..."
    session_key_short.short_description = 'Session Key'
    
    def is_expired(self, obj):
        from django.utils import timezone
        return obj.expire_date < timezone.now()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """Admin interface for Django Admin Log Entries"""
    list_display = ['action_time', 'user', 'content_type', 'object_repr', 'action_flag_display']
    list_filter = ['action_flag', 'action_time', 'content_type']
    search_fields = ['object_repr', 'change_message', 'user__email']
    ordering = ['-action_time']
    readonly_fields = ['action_time', 'user', 'content_type', 'object_id', 'object_repr', 'action_flag', 'change_message']
    
    def action_flag_display(self, obj):
        flags = {1: 'Added', 2: 'Changed', 3: 'Deleted'}
        return flags.get(obj.action_flag, 'Unknown')
    action_flag_display.short_description = 'Action'
