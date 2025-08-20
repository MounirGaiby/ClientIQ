from django.urls import path
from . import views

urlpatterns = [
    path('validate/<str:subdomain>/', views.validate_tenant, name='validate_tenant'),
]
