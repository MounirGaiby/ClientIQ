"""
Activities app configuration.
"""

from django.apps import AppConfig


class ActivitiesConfig(AppConfig):
    """Configuration for activities app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.activities'
    verbose_name = 'Activities & Follow-up'
    
    def ready(self):
        """Import signal handlers when app is ready."""
        import apps.activities.signals