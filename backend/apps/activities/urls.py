"""
URL configuration for activities app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ActivityTypeViewSet,
    ActivityViewSet,
    TaskViewSet,
    InteractionLogViewSet,
    FollowUpRuleViewSet,
    DashboardStatsView,
    ContactActivityListView,
    ContactInteractionListView,
    OpportunityActivityListView,
    OpportunityInteractionListView
)

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'activity-types', ActivityTypeViewSet, basename='activitytype')
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'interactions', InteractionLogViewSet, basename='interactionlog')
router.register(r'follow-up-rules', FollowUpRuleViewSet, basename='followuprule')

# Define URL patterns
urlpatterns = [
    # Router URLs
    path('api/', include(router.urls)),
    
    # Dashboard and statistics
    path('api/dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    
    # Contact-specific views
    path('api/contacts/<int:contact_id>/activities/', 
         ContactActivityListView.as_view(), 
         name='contact-activities'),
    path('api/contacts/<int:contact_id>/interactions/', 
         ContactInteractionListView.as_view(), 
         name='contact-interactions'),
    
    # Opportunity-specific views
    path('api/opportunities/<int:opportunity_id>/activities/', 
         OpportunityActivityListView.as_view(), 
         name='opportunity-activities'),
    path('api/opportunities/<int:opportunity_id>/interactions/', 
         OpportunityInteractionListView.as_view(), 
         name='opportunity-interactions'),
]