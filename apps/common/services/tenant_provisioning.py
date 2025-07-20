"""
Tenant Provisioning Service

Service-Oriented Architecture (SOA) implementation for tenant management.
Handles tenant creation, schema setup, and initial configuration.
"""

import logging
from typing import Dict, Any, Optional
from django.db import transaction
from django.utils.text import slugify
from apps.tenants.models import Tenant, Domain
from apps.demo.models import DemoRequest

logger = logging.getLogger(__name__)


class TenantProvisioningService:
    """
    Service for provisioning new tenants from demo requests.
    
    This service follows SOA principles by encapsulating all tenant
    provisioning logic in a single, reusable service class.
    """
    
    @staticmethod
    def generate_schema_name(company_name: str) -> str:
        """
        Generate a valid schema name from company name.
        
        Args:
            company_name: Name of the company
            
        Returns:
            Valid PostgreSQL schema name
        """
        # Convert to lowercase and replace spaces/special chars with underscores
        schema_name = slugify(company_name).replace('-', '_')
        
        # Ensure it starts with a letter (PostgreSQL requirement)
        if schema_name and not schema_name[0].isalpha():
            schema_name = f"tenant_{schema_name}"
        
        # Truncate to max 63 characters (PostgreSQL limit)
        schema_name = schema_name[:63]
        
        # Ensure uniqueness by checking existing tenants
        base_name = schema_name
        counter = 1
        while Tenant.objects.filter(schema_name=schema_name).exists():
            schema_name = f"{base_name}_{counter}"
            if len(schema_name) > 63:
                # Truncate base name to make room for counter
                truncated_base = base_name[:60-len(str(counter))]
                schema_name = f"{truncated_base}_{counter}"
            counter += 1
        
        return schema_name
    
    @staticmethod
    def generate_domain_name(company_name: str, base_domain: str = "localhost") -> str:
        """
        Generate a unique domain name for the tenant.
        
        Args:
            company_name: Name of the company
            base_domain: Base domain to use (default: localhost for development)
            
        Returns:
            Unique domain name for the tenant
        """
        subdomain = slugify(company_name)
        domain_name = f"{subdomain}.{base_domain}"
        
        # Ensure uniqueness by checking existing domains
        base_name = subdomain
        counter = 1
        while Domain.objects.filter(domain=domain_name).exists():
            domain_name = f"{base_name}-{counter}.{base_domain}"
            counter += 1
        
        return domain_name
    
    @classmethod
    @transaction.atomic
    def create_tenant_from_demo(cls, demo_request: DemoRequest) -> Tenant:
        """
        Create a new tenant from an approved demo request.
        
        Args:
            demo_request: Approved demo request to convert
            
        Returns:
            Newly created tenant
            
        Raises:
            ValueError: If demo request is not approved
            Exception: If tenant creation fails
        """
        if demo_request.status != 'approved':
            raise ValueError("Demo request must be approved before creating tenant")
        
        logger.info(f"Creating tenant from demo request: {demo_request.company_name}")
        
        try:
            # Generate schema name
            schema_name = cls.generate_schema_name(demo_request.company_name)
            
            # Create tenant
            tenant = Tenant.objects.create(
                schema_name=schema_name,
                name=demo_request.company_name,
                contact_email=demo_request.contact_email,
                contact_phone=demo_request.contact_phone,
                subscription_status='trial',
                is_active=True
            )
            
            # Create primary domain
            domain_name = cls.generate_domain_name(demo_request.company_name)
            Domain.objects.create(
                tenant=tenant,
                domain=domain_name,
                is_primary=True
            )
            
            # Update demo request status
            demo_request.status = 'converted'
            demo_request.admin_notes = f"Converted to tenant: {tenant.name} (schema: {schema_name})"
            demo_request.save()
            
            logger.info(
                f"Successfully created tenant: {tenant.name} "
                f"(schema: {schema_name}, domain: {domain_name})"
            )
            
            return tenant
            
        except Exception as e:
            logger.error(f"Failed to create tenant from demo request {demo_request.id}: {str(e)}")
            raise
    
    @classmethod
    def get_tenant_info(cls, tenant: Tenant) -> Dict[str, Any]:
        """
        Get comprehensive information about a tenant.
        
        Args:
            tenant: Tenant instance
            
        Returns:
            Dictionary with tenant information
        """
        return {
            'id': tenant.id,
            'name': tenant.name,
            'schema_name': tenant.schema_name,
            'contact_email': tenant.contact_email,
            'contact_phone': tenant.contact_phone,
            'subscription_status': tenant.subscription_status,
            'is_active': tenant.is_active,
            'created_on': tenant.created_on,
            'domains': [
                {
                    'domain': domain.domain,
                    'is_primary': domain.is_primary
                }
                for domain in tenant.domains.all()
            ]
        }
    
    @classmethod
    def validate_tenant_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate tenant creation data.
        
        Args:
            data: Tenant data to validate
            
        Returns:
            Validated and cleaned data
            
        Raises:
            ValueError: If validation fails
        """
        required_fields = ['company_name', 'contact_email']
        
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f"Field '{field}' is required")
        
        # Validate email format
        from django.core.validators import EmailValidator
        from django.core.exceptions import ValidationError
        
        email_validator = EmailValidator()
        try:
            email_validator(data['contact_email'])
        except ValidationError:
            raise ValueError("Invalid email format")
        
        return data
