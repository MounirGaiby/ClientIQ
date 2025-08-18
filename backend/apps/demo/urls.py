"""
URL configuration for demo app.
"""
from django.urls import path
from . import views

app_name = 'demo'

urlpatterns = [
    path('requests/', views.DemoRequestListCreateView.as_view(), name='demo-request-list-create'),
    path('requests/<int:pk>/', views.DemoRequestDetailView.as_view(), name='demo-request-detail'),
]
