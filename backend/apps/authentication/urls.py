"""
URL configuration for authentication app.
"""
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('me/', views.CurrentUserView.as_view(), name='current_user'),
]
