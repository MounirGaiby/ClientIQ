"""
URL configuration for tenants app.
"""
from django.urls import path
from . import views

app_name = 'tenants'

urlpatterns = [
    path('', views.TenantListView.as_view(), name='tenant-list'),
    path('<int:pk>/', views.TenantDetailView.as_view(), name='tenant-detail'),
    path('current/', views.CurrentTenantView.as_view(), name='current-tenant'),
]
