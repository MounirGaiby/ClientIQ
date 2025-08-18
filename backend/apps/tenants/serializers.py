"""
Serializers for tenants app.
"""
from rest_framework import serializers
from .models import Tenant, Domain


class DomainSerializer(serializers.ModelSerializer):
    """
    Serializer for Domain model.
    """
    
    class Meta:
        model = Domain
        fields = ['id', 'domain', 'is_primary']


class TenantSerializer(serializers.ModelSerializer):
    """
    Serializer for Tenant model.
    """
    domains = DomainSerializer(many=True, read_only=True)
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'schema_name', 'name', 'description', 
            'contact_email', 'contact_phone', 'subscription_status',
            'is_active', 'created_on', 'domains'
        ]
        read_only_fields = ['id', 'schema_name', 'created_on']


class TenantCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating tenants.
    """
    primary_domain = serializers.CharField(write_only=True)
    
    class Meta:
        model = Tenant
        fields = [
            'name', 'description', 'contact_email', 
            'contact_phone', 'primary_domain'
        ]
    
    def create(self, validated_data):
        primary_domain = validated_data.pop('primary_domain')
        tenant = Tenant.objects.create(**validated_data)
        
        # Create the primary domain
        Domain.objects.create(
            domain=primary_domain,
            tenant=tenant,
            is_primary=True
        )
        
        return tenant
