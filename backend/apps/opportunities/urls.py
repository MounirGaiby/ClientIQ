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
    path('api/', include(router.urls)),
]