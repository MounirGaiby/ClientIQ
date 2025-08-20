"""
URL configuration for contacts app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'contacts'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'companies', views.CompanyViewSet, basename='company')
router.register(r'tags', views.ContactTagViewSet, basename='contact-tag')
router.register(r'contacts', views.ContactViewSet, basename='contact')

urlpatterns = [
    # ViewSet URLs through router
    path('api/', include(router.urls)),
    
    # Legacy function-based view URLs (for simpler access patterns)
    path('', views.ContactListCreateView.as_view(), name='contact-list-create'),
    path('<int:pk>/', views.ContactDetailView.as_view(), name='contact-detail'),
]
