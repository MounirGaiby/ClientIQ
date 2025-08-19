from django.apps import AppConfig


class TenantPermissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tenant_permissions'
    verbose_name = 'Tenant Permissions'
