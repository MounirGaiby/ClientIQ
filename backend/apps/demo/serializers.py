"""
Serializers for demo app.
"""
from rest_framework import serializers
from .models import DemoRequest


class DemoRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for DemoRequest model.
    """
    
    class Meta:
        model = DemoRequest
        fields = [
            'id', 'company_name', 'first_name', 'last_name', 
            'email', 'phone', 'job_title', 'company_size', 
            'industry', 'message', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'created_at']


class DemoRequestCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating demo requests.
    """
    
    class Meta:
        model = DemoRequest
        fields = [
            'company_name', 'first_name', 'last_name', 
            'email', 'phone', 'job_title', 'company_size', 
            'industry', 'message'
        ]
    
    def validate_email(self, value):
        """
        Check if email is already registered for a pending/processing request.
        """
        pending_statuses = ['pending', 'processing']
        if DemoRequest.objects.filter(
            email=value, 
            status__in=pending_statuses
        ).exists():
            raise serializers.ValidationError(
                "A demo request with this email is already being processed."
            )
        return value


class DemoRequestAdminSerializer(serializers.ModelSerializer):
    """
    Serializer for admin demo request management.
    """
    
    class Meta:
        model = DemoRequest
        fields = [
            'id', 'company_name', 'first_name', 'last_name', 
            'email', 'phone', 'job_title', 'company_size', 
            'industry', 'message', 'status', 'tenant', 
            'notes', 'admin_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
