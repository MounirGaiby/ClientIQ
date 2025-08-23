"""
App configuration for opportunities app.
"""
from django.apps import AppConfig


class OpportunitiesConfig(AppConfig):
    """Configuration for the opportunities app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.opportunities'
    verbose_name = 'Sales Pipeline & Opportunities'
    
    def ready(self):
        """Import signal handlers when app is ready."""
        # Signals will be imported here when created
        pass