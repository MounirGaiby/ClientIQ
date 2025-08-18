"""
Views for tenants app.
"""
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django_tenants.utils import get_tenant_model, get_public_schema_name
from django.db import connection

from .models import Tenant
from .serializers import TenantSerializer, TenantCreateSerializer


class TenantListView(generics.ListCreateAPIView):
    """
    List all tenants or create a new one (superuser only).
    """
    queryset = Tenant.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TenantCreateSerializer
        return TenantSerializer
    
    def get_queryset(self):
        # Only superusers can see all tenants
        if self.request.user.is_superuser:
            return Tenant.objects.all()
        return Tenant.objects.none()


class TenantDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a tenant (superuser only).
    """
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only superusers can manage tenants
        if self.request.user.is_superuser:
            return Tenant.objects.all()
        return Tenant.objects.none()


class CurrentTenantView(APIView):
    """
    Get information about the current tenant.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get current tenant from connection
        tenant = connection.tenant
        
        if tenant.schema_name == get_public_schema_name():
            return Response({
                "success": False,
                "error": "Not in a tenant context"
            }, status=400)
        
        serializer = TenantSerializer(tenant)
        return Response({
            "success": True,
            "data": serializer.data
        })
