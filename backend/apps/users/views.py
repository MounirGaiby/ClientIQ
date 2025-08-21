"""
Views for users app.
"""
from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import CustomUser
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer


class UserListCreateView(generics.ListCreateAPIView):
    """
    List all users in the current tenant or create a new one.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        # Debug authentication and tenant context
        print(f"DEBUG - Request user: {request.user}")
        print(f"DEBUG - User authenticated: {request.user.is_authenticated}")
        print(f"DEBUG - User ID: {getattr(request.user, 'id', 'None')}")
        print(f"DEBUG - Tenant: {getattr(request, 'tenant', 'None')}")
        print(f"DEBUG - Authorization header: {request.META.get('HTTP_AUTHORIZATION', 'None')}")
        
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        # Debug: Print user info
        print(f"DEBUG - User: {self.request.user}")
        print(f"DEBUG - User authenticated: {self.request.user.is_authenticated}")
        print(f"DEBUG - Tenant: {getattr(self.request, 'tenant', None)}")
        
        # Return users for the current tenant only
        return CustomUser.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CustomUser.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


class CurrentUserDetailView(generics.RetrieveUpdateAPIView):
    """
    Get or update current user's information.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer
