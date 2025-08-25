"""
URL configuration for opportunities app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'stages', views.SalesStageViewSet, basename='salesstage')
router.register(r'opportunities', views.OpportunityViewSet, basename='opportunity')

app_name = 'opportunities'

urlpatterns = [
    path('', include(router.urls)),
    path('pipeline/', views.OpportunityViewSet.as_view({'get': 'pipeline'}), name='pipeline'),
    path('analytics/', views.OpportunityViewSet.as_view({'get': 'analytics'}), name='analytics'),
]