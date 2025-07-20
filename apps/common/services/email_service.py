"""
Email Notification Service

Service-Oriented Architecture (SOA) implementation for email notifications.
Handles sending welcome emails, password notifications, and system alerts.
"""

import logging
from typing import Dict, Any, Optional, List
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from apps.users.models import TenantUser
from apps.tenants.models import Tenant

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for handling all email communications.
    
    This service follows SOA principles by encapsulating all email
    logic in a single, reusable service class.
    """
    
    @staticmethod
    def send_welcome_email(user: TenantUser, tenant: Tenant, password: str) -> Dict[str, Any]:
        """
        Send welcome email to new user with login credentials.
        
        Args:
            user: TenantUser instance
            tenant: Tenant instance
            password: Generated password for the user
            
        Returns:
            Dictionary with email sending status
        """
        logger.info(f"Sending welcome email to {user.email} for tenant {tenant.name}")
        
        try:
            # Email context
            context = {
                'user': user,
                'tenant': tenant,
                'password': password,
                'login_url': f"http://{tenant.get_primary_domain()}/admin/",
                'company_name': 'ClientIQ',
                'support_email': 'support@clientiq.com'
            }
            
            # Email content
            subject = f"Welcome to {tenant.name} - Your Account Details"
            
            # HTML content
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #4a90e2; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .credentials {{ background-color: #e8f4f8; padding: 15px; border-left: 4px solid #4a90e2; margin: 20px 0; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                    .button {{ background-color: #4a90e2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to {tenant.name}!</h1>
                    </div>
                    
                    <div class="content">
                        <h2>Hello {user.get_full_name()},</h2>
                        
                        <p>Your account has been successfully created for <strong>{tenant.name}</strong>. We're excited to have you on board!</p>
                        
                        <div class="credentials">
                            <h3>Your Login Credentials:</h3>
                            <p><strong>Email:</strong> {user.email}</p>
                            <p><strong>Password:</strong> {password}</p>
                            <p><strong>Login URL:</strong> <a href="{context['login_url']}">{context['login_url']}</a></p>
                        </div>
                        
                        <p><strong>Important Security Note:</strong> Please change your password after your first login for security purposes.</p>
                        
                        <p>Your role: <strong>{user.user_type.title()}</strong></p>
                        
                        <a href="{context['login_url']}" class="button">Login to Your Account</a>
                        
                        <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
                    </div>
                    
                    <div class="footer">
                        <p>Best regards,<br>The ClientIQ Team</p>
                        <p>Support: {context['support_email']}</p>
                        <p>This email was sent to {user.email}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text content (fallback)
            text_content = f"""
Welcome to {tenant.name}!

Hello {user.get_full_name()},

Your account has been successfully created for {tenant.name}. We're excited to have you on board!

Your Login Credentials:
Email: {user.email}
Password: {password}
Login URL: {context['login_url']}

Important Security Note: Please change your password after your first login for security purposes.

Your role: {user.user_type.title()}

If you have any questions or need assistance, please don't hesitate to contact our support team.

Best regards,
The ClientIQ Team

Support: {context['support_email']}
This email was sent to {user.email}
            """
            
            # Send email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@clientiq.com'),
                to=[user.email]
            )
            email.attach_alternative(html_content, "text/html")
            
            # For development/testing, we'll log the email instead of sending
            if getattr(settings, 'EMAIL_BACKEND', '') == 'django.core.mail.backends.console.EmailBackend':
                logger.info("EMAIL BACKEND: Console - Email will be displayed in console")
                email.send()
                return {
                    'success': True,
                    'message': f"Welcome email sent to {user.email} (console backend)",
                    'email_data': {
                        'to': user.email,
                        'subject': subject,
                        'tenant': tenant.name
                    }
                }
            else:
                # In production, this would actually send the email
                email.send()
                return {
                    'success': True,
                    'message': f"Welcome email sent to {user.email}",
                    'email_data': {
                        'to': user.email,
                        'subject': subject,
                        'tenant': tenant.name
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
            return {
                'success': False,
                'message': f"Failed to send email: {str(e)}",
                'error': str(e)
            }
    
    @staticmethod
    def send_password_reset_email(user: TenantUser, tenant: Tenant, new_password: str) -> Dict[str, Any]:
        """
        Send password reset email to user.
        
        Args:
            user: TenantUser instance
            tenant: Tenant instance
            new_password: New password for the user
            
        Returns:
            Dictionary with email sending status
        """
        logger.info(f"Sending password reset email to {user.email}")
        
        try:
            subject = f"Password Reset - {tenant.name}"
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #e74c3c; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .credentials {{ background-color: #fdf2e8; padding: 15px; border-left: 4px solid #e74c3c; margin: 20px 0; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Password Reset</h1>
                    </div>
                    
                    <div class="content">
                        <h2>Hello {user.get_full_name()},</h2>
                        
                        <p>Your password has been reset for your account in <strong>{tenant.name}</strong>.</p>
                        
                        <div class="credentials">
                            <h3>Your New Credentials:</h3>
                            <p><strong>Email:</strong> {user.email}</p>
                            <p><strong>New Password:</strong> {new_password}</p>
                        </div>
                        
                        <p><strong>Important:</strong> Please log in and change this password immediately for security purposes.</p>
                    </div>
                    
                    <div class="footer">
                        <p>Best regards,<br>The ClientIQ Team</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
Password Reset

Hello {user.get_full_name()},

Your password has been reset for your account in {tenant.name}.

Your New Credentials:
Email: {user.email}
New Password: {new_password}

Important: Please log in and change this password immediately for security purposes.

Best regards,
The ClientIQ Team
            """
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@clientiq.com'),
                to=[user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            return {
                'success': True,
                'message': f"Password reset email sent to {user.email}",
                'email_data': {
                    'to': user.email,
                    'subject': subject,
                    'tenant': tenant.name
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
            return {
                'success': False,
                'message': f"Failed to send email: {str(e)}",
                'error': str(e)
            }
    
    @staticmethod
    def send_admin_notification(tenant: Tenant, subject: str, message: str, 
                               recipient_emails: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Send notification email to tenant administrators.
        
        Args:
            tenant: Tenant instance
            subject: Email subject
            message: Email message
            recipient_emails: Optional list of specific emails to send to
            
        Returns:
            Dictionary with email sending status
        """
        logger.info(f"Sending admin notification for tenant {tenant.name}")
        
        try:
            # Get admin users if no specific recipients provided
            if not recipient_emails:
                from django_tenants.utils import schema_context
                with schema_context(tenant.schema_name):
                    admin_users = TenantUser.objects.filter(
                        is_tenant_admin=True,
                        is_active=True
                    )
                    recipient_emails = [user.email for user in admin_users]
            
            if not recipient_emails:
                return {
                    'success': False,
                    'message': "No recipient emails found",
                    'error': "No admin users or recipient emails provided"
                }
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: #2c3e50; color: white; padding: 20px; text-align: center;">
                        <h1>Admin Notification - {tenant.name}</h1>
                    </div>
                    
                    <div style="padding: 20px; background-color: #f9f9f9;">
                        <p>{message}</p>
                    </div>
                    
                    <div style="padding: 20px; text-align: center; color: #666; font-size: 12px;">
                        <p>The ClientIQ Team</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            email = EmailMultiAlternatives(
                subject=f"[{tenant.name}] {subject}",
                body=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@clientiq.com'),
                to=recipient_emails
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            return {
                'success': True,
                'message': f"Admin notification sent to {len(recipient_emails)} recipients",
                'email_data': {
                    'recipients': recipient_emails,
                    'subject': subject,
                    'tenant': tenant.name
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to send admin notification: {str(e)}")
            return {
                'success': False,
                'message': f"Failed to send notification: {str(e)}",
                'error': str(e)
            }
    
    @staticmethod
    def get_email_status() -> Dict[str, Any]:
        """
        Get email configuration status.
        
        Returns:
            Dictionary with email configuration information
        """
        return {
            'backend': getattr(settings, 'EMAIL_BACKEND', 'Not configured'),
            'host': getattr(settings, 'EMAIL_HOST', 'Not configured'),
            'port': getattr(settings, 'EMAIL_PORT', 'Not configured'),
            'use_tls': getattr(settings, 'EMAIL_USE_TLS', False),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not configured'),
            'status': 'Console backend (development)' if getattr(settings, 'EMAIL_BACKEND', '') == 'django.core.mail.backends.console.EmailBackend' else 'Production backend'
        }
