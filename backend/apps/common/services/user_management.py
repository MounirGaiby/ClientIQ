"""
User Management Service

Service-Oriented Architecture (SOA) implementation for user management.
Handles user creation, password generation, and admin user setup.
"""

import logging
import secrets
import string
from typing import Dict, Any, Optional
from django.db import transaction
from django.contrib.auth.hashers import make_password
from apps.users.models import TenantUser
from apps.tenants.models import Tenant
from apps.common.services.permission_service import PermissionService
from django_tenants.utils import schema_context

logger = logging.getLogger(__name__)


class UserManagementService:
    """
    Service for managing users within tenants.
    
    This service follows SOA principles by encapsulating all user
    management logic in a single, reusable service class.
    """
    
    @staticmethod
    def generate_secure_password(length: int = 12) -> str:
        """
        Generate a secure random password.
        
        Args:
            length: Length of the password (default: 12)
            
        Returns:
            Secure random password
        """
        # Define character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = "!@#$%^&*"
        
        # Ensure at least one character from each set
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(symbols)
        ]
        
        # Fill remaining length with random characters from all sets
        all_characters = lowercase + uppercase + digits + symbols
        for _ in range(length - 4):
            password.append(secrets.choice(all_characters))
        
        # Shuffle the password list
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    @classmethod
    @transaction.atomic
    def create_tenant_admin_user(cls, tenant: Tenant, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an admin user for a tenant.
        
        Args:
            tenant: Tenant instance
            user_data: Dictionary with user information
                Required: first_name, last_name, email
                Optional: phone_number, job_title, department
                
        Returns:
            Dictionary with user info and generated password
            
        Raises:
            ValueError: If required data is missing or invalid
        """
        logger.info(f"Creating admin user for tenant: {tenant.name}")
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email']
        for field in required_fields:
            if not user_data.get(field):
                raise ValueError(f"Field '{field}' is required")
        
        # Generate secure password
        password = cls.generate_secure_password()
        
        # Create user in tenant schema
        with schema_context(tenant.schema_name):
            try:
                # Check if user with this email already exists
                if TenantUser.objects.filter(email=user_data['email']).exists():
                    raise ValueError(f"User with email {user_data['email']} already exists in this tenant")
                
                # Create the user
                user = TenantUser.objects.create(
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    phone_number=user_data.get('phone_number', ''),
                    job_title=user_data.get('job_title', 'Administrator'),
                    department=user_data.get('department', 'Administration'),
                    user_type='admin',
                    is_tenant_admin=True,
                    is_active=True,
                    is_staff=True,  # Allow admin interface access
                    password=make_password(password)
                )
                
                # Assign admin role
                PermissionService.assign_admin_role(user, tenant)
                
                logger.info(f"Successfully created admin user: {user.email}")
                
                return {
                    'user': user,
                    'password': password,
                    'tenant': tenant,
                    'success': True,
                    'message': f"Admin user created successfully for {tenant.name}"
                }
                
            except Exception as e:
                logger.error(f"Failed to create admin user for tenant {tenant.name}: {str(e)}")
                raise
    
    @classmethod
    def create_regular_user(cls, tenant: Tenant, user_data: Dict[str, Any], 
                           created_by: TenantUser) -> Dict[str, Any]:
        """
        Create a regular user for a tenant.
        
        Args:
            tenant: Tenant instance
            user_data: Dictionary with user information
            created_by: User creating this user (for audit trail)
            
        Returns:
            Dictionary with user info and generated password
        """
        logger.info(f"Creating regular user for tenant: {tenant.name}")
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email']
        for field in required_fields:
            if not user_data.get(field):
                raise ValueError(f"Field '{field}' is required")
        
        # Generate secure password
        password = cls.generate_secure_password()
        
        # Create user in tenant schema
        with schema_context(tenant.schema_name):
            try:
                # Check if user with this email already exists
                if TenantUser.objects.filter(email=user_data['email']).exists():
                    raise ValueError(f"User with email {user_data['email']} already exists in this tenant")
                
                # Create the user
                user = TenantUser.objects.create(
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    phone_number=user_data.get('phone_number', ''),
                    job_title=user_data.get('job_title', ''),
                    department=user_data.get('department', ''),
                    user_type=user_data.get('user_type', 'user'),
                    is_tenant_admin=False,
                    is_active=True,
                    is_staff=False,
                    password=make_password(password)
                )
                
                # Assign role based on user type
                role_name = user_data.get('role', 'User')  # Default to User role
                if role_name in ['Admin', 'Manager', 'User']:
                    from apps.tenant_permissions.models import TenantRole, TenantUserRole
                    
                    try:
                        role = TenantRole.objects.get(name=role_name)
                        TenantUserRole.objects.create(
                            user=user,
                            role=role,
                            assigned_by=created_by,
                            is_active=True
                        )
                    except TenantRole.DoesNotExist:
                        logger.warning(f"Role {role_name} not found, user created without role")
                
                logger.info(f"Successfully created user: {user.email}")
                
                return {
                    'user': user,
                    'password': password,
                    'tenant': tenant,
                    'success': True,
                    'message': f"User created successfully for {tenant.name}"
                }
                
            except Exception as e:
                logger.error(f"Failed to create user for tenant {tenant.name}: {str(e)}")
                raise
    
    @staticmethod
    def get_user_info(user: TenantUser, tenant: Tenant) -> Dict[str, Any]:
        """
        Get comprehensive information about a user.
        
        Args:
            user: TenantUser instance
            tenant: Tenant instance
            
        Returns:
            Dictionary with user information
        """
        with schema_context(tenant.schema_name):
            from apps.tenant_permissions.models import TenantUserRole
            
            # Get user roles
            user_roles = TenantUserRole.objects.filter(
                user=user,
                is_active=True
            ).select_related('role__role_group')
            
            return {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
                'phone_number': user.phone_number,
                'job_title': user.job_title,
                'department': user.department,
                'user_type': user.user_type,
                'is_tenant_admin': user.is_tenant_admin,
                'is_active': user.is_active,
                'date_joined': user.date_joined,
                'last_login': user.last_login,
                'roles': [
                    {
                        'name': ur.role.name,
                        'role_group': ur.role.role_group.name,
                        'assigned_at': ur.assigned_at
                    }
                    for ur in user_roles
                ],
                'permissions': user.get_permissions(),
                'tenant': {
                    'name': tenant.name,
                    'schema_name': tenant.schema_name
                }
            }
    
    @staticmethod
    def validate_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate user creation data.
        
        Args:
            data: User data to validate
            
        Returns:
            Validated and cleaned data
            
        Raises:
            ValueError: If validation fails
        """
        required_fields = ['first_name', 'last_name', 'email']
        
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f"Field '{field}' is required")
            
            # Basic validation
            if field in ['first_name', 'last_name'] and len(data[field].strip()) < 2:
                raise ValueError(f"Field '{field}' must be at least 2 characters long")
        
        # Validate email format
        from django.core.validators import EmailValidator
        from django.core.exceptions import ValidationError
        
        email_validator = EmailValidator()
        try:
            email_validator(data['email'])
        except ValidationError:
            raise ValueError("Invalid email format")
        
        # Clean data
        cleaned_data = {
            'first_name': data['first_name'].strip().title(),
            'last_name': data['last_name'].strip().title(),
            'email': data['email'].strip().lower(),
            'phone_number': data.get('phone_number', '').strip(),
            'job_title': data.get('job_title', '').strip(),
            'department': data.get('department', '').strip(),
            'user_type': data.get('user_type', 'user'),
            'role': data.get('role', 'User')
        }
        
        return cleaned_data
