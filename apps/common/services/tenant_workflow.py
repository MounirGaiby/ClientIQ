"""
Tenant Workflow Service

Complete workflow orchestration service that handles the entire process:
Demo Request → Tenant Creation → User Setup → Email Notifications

This service follows SOA principles by coordinating between other services.
"""

import logging
from typing import Dict, Any, Optional
from django.db import transaction
from apps.demo.models import DemoRequest
from apps.tenants.models import Tenant
from apps.users.models import TenantUser
from apps.common.services.tenant_provisioning import TenantProvisioningService
from apps.common.services.user_management import UserManagementService
from apps.common.services.email_service import EmailService

logger = logging.getLogger(__name__)


class TenantWorkflowService:
    """
    Orchestrates the complete tenant provisioning workflow.
    
    This service coordinates between multiple services to provide
    a complete end-to-end workflow for tenant creation and setup.
    """
    
    @classmethod
    @transaction.atomic
    def process_demo_request(cls, demo_request_id: int) -> Dict[str, Any]:
        """
        Complete workflow: Process demo request and create tenant with admin user.
        
        Args:
            demo_request_id: ID of the DemoRequest to process
            
        Returns:
            Dictionary with workflow results
        """
        logger.info(f"Starting demo request workflow for ID: {demo_request_id}")
        
        try:
            # Step 1: Get demo request
            try:
                demo_request = DemoRequest.objects.get(id=demo_request_id)
            except DemoRequest.DoesNotExist:
                raise ValueError(f"Demo request with ID {demo_request_id} not found")
            
            if demo_request.status != 'pending':
                raise ValueError(f"Demo request is not pending (current status: {demo_request.status})")
            
            # Step 2: Update demo request status
            demo_request.status = 'processing'
            demo_request.save()
            
            workflow_results = {
                'demo_request': demo_request,
                'steps': []
            }
            
            # Step 3: Create tenant
            logger.info("Step 1: Creating tenant")
            tenant_data = {
                'name': demo_request.company_name,
                'description': f"Tenant for {demo_request.company_name}",
                'subscription_status': 'trial'
            }
            
            tenant_result = TenantProvisioningService.create_tenant_with_setup(tenant_data)
            
            if not tenant_result['success']:
                demo_request.status = 'failed'
                demo_request.notes = f"Tenant creation failed: {tenant_result['message']}"
                demo_request.save()
                raise Exception(f"Tenant creation failed: {tenant_result['message']}")
            
            tenant = tenant_result['tenant']
            workflow_results['steps'].append({
                'step': 'tenant_creation',
                'success': True,
                'data': tenant_result
            })
            
            # Step 4: Create admin user
            logger.info("Step 2: Creating admin user")
            user_data = {
                'first_name': demo_request.first_name,
                'last_name': demo_request.last_name,
                'email': demo_request.email,
                'phone_number': demo_request.phone,
                'job_title': demo_request.job_title,
                'department': 'Administration'
            }
            
            # Validate user data
            validated_user_data = UserManagementService.validate_user_data(user_data)
            
            user_result = UserManagementService.create_tenant_admin_user(
                tenant, validated_user_data
            )
            
            if not user_result['success']:
                demo_request.status = 'failed'
                demo_request.notes = f"User creation failed: {user_result['message']}"
                demo_request.save()
                raise Exception(f"User creation failed: {user_result['message']}")
            
            admin_user = user_result['user']
            password = user_result['password']
            workflow_results['steps'].append({
                'step': 'user_creation',
                'success': True,
                'data': user_result
            })
            
            # Step 5: Send welcome email
            logger.info("Step 3: Sending welcome email")
            email_result = EmailService.send_welcome_email(admin_user, tenant, password)
            
            workflow_results['steps'].append({
                'step': 'email_notification',
                'success': email_result['success'],
                'data': email_result
            })
            
            # Step 6: Update demo request with success
            demo_request.status = 'approved'
            demo_request.tenant = tenant
            demo_request.notes = f"Successfully created tenant and admin user. Email sent to {admin_user.email}"
            demo_request.save()
            
            # Final result
            workflow_results.update({
                'success': True,
                'tenant': tenant,
                'admin_user': admin_user,
                'password': password,  # Note: In production, this should be handled securely
                'email_sent': email_result['success'],
                'message': f"Successfully processed demo request for {demo_request.company_name}"
            })
            
            logger.info(f"Demo request workflow completed successfully for {demo_request.company_name}")
            return workflow_results
            
        except Exception as e:
            logger.error(f"Demo request workflow failed: {str(e)}")
            
            # Update demo request status on failure
            try:
                demo_request = DemoRequest.objects.get(id=demo_request_id)
                demo_request.status = 'failed'
                if not demo_request.notes:
                    demo_request.notes = f"Workflow failed: {str(e)}"
                demo_request.save()
            except:
                pass  # Don't fail if we can't update the demo request
            
            return {
                'success': False,
                'message': f"Workflow failed: {str(e)}",
                'error': str(e),
                'demo_request_id': demo_request_id
            }
    
    @staticmethod
    def get_workflow_status(demo_request_id: int) -> Dict[str, Any]:
        """
        Get the status of a demo request workflow.
        
        Args:
            demo_request_id: ID of the DemoRequest
            
        Returns:
            Dictionary with workflow status
        """
        try:
            demo_request = DemoRequest.objects.get(id=demo_request_id)
            
            result = {
                'demo_request_id': demo_request_id,
                'status': demo_request.status,
                'company_name': demo_request.company_name,
                'contact_email': demo_request.email,
                'created_at': demo_request.created_at,
                'updated_at': demo_request.updated_at,
                'notes': demo_request.notes
            }
            
            # If tenant was created, include tenant info
            if demo_request.tenant:
                result['tenant'] = {
                    'id': demo_request.tenant.id,
                    'name': demo_request.tenant.name,
                    'schema_name': demo_request.tenant.schema_name,
                    'domain': demo_request.tenant.get_primary_domain()
                }
                
                # Get admin user info
                from django_tenants.utils import schema_context
                with schema_context(demo_request.tenant.schema_name):
                    admin_users = TenantUser.objects.filter(
                        is_tenant_admin=True,
                        email=demo_request.email
                    ).first()
                    
                    if admin_users:
                        result['admin_user'] = {
                            'email': admin_users.email,
                            'full_name': admin_users.get_full_name(),
                            'is_active': admin_users.is_active,
                            'date_joined': admin_users.date_joined,
                            'last_login': admin_users.last_login
                        }
            
            return result
            
        except DemoRequest.DoesNotExist:
            return {
                'success': False,
                'message': f"Demo request with ID {demo_request_id} not found"
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to get workflow status: {str(e)}",
                'error': str(e)
            }
    
    @staticmethod
    def list_pending_demo_requests() -> Dict[str, Any]:
        """
        List all pending demo requests.
        
        Returns:
            Dictionary with list of pending demo requests
        """
        try:
            pending_requests = DemoRequest.objects.filter(status='pending').order_by('-created_at')
            
            return {
                'success': True,
                'count': pending_requests.count(),
                'requests': [
                    {
                        'id': req.id,
                        'company_name': req.company_name,
                        'contact_name': f"{req.first_name} {req.last_name}",
                        'email': req.email,
                        'phone': req.phone,
                        'job_title': req.job_title,
                        'company_size': req.company_size,
                        'industry': req.industry,
                        'created_at': req.created_at,
                        'message': req.message
                    }
                    for req in pending_requests
                ]
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to list pending requests: {str(e)}",
                'error': str(e)
            }
    
    @staticmethod
    def bulk_process_demo_requests(demo_request_ids: list) -> Dict[str, Any]:
        """
        Process multiple demo requests in bulk.
        
        Args:
            demo_request_ids: List of demo request IDs to process
            
        Returns:
            Dictionary with bulk processing results
        """
        logger.info(f"Starting bulk processing for {len(demo_request_ids)} demo requests")
        
        results = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'results': []
        }
        
        for demo_id in demo_request_ids:
            try:
                result = TenantWorkflowService.process_demo_request(demo_id)
                
                if result['success']:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                
                results['results'].append({
                    'demo_request_id': demo_id,
                    'success': result['success'],
                    'message': result['message']
                })
                
            except Exception as e:
                results['failed'] += 1
                results['results'].append({
                    'demo_request_id': demo_id,
                    'success': False,
                    'message': f"Failed: {str(e)}"
                })
            
            results['total_processed'] += 1
        
        logger.info(f"Bulk processing completed: {results['successful']} successful, {results['failed']} failed")
        return results
