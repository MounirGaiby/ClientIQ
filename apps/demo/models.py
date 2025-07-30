from django.db import models

from django.db import models
from django.core.validators import EmailValidator


class DemoRequest(models.Model):
    """
    Model for storing demo requests from potential customers.
    This stays in the public schema as it's shared data.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('processing', 'Processing'),
        ('approved', 'Approved'),
        ('converted', 'Converted to Tenant'),
        ('failed', 'Failed'),
        ('rejected', 'Rejected'),
    ]
    
    # Company information
    company_name = models.CharField(
        max_length=100,
        help_text="Name of the company requesting demo"
    )
    
    # Contact information
    first_name = models.CharField(
        max_length=50,
        help_text="First name of the contact person"
    )
    last_name = models.CharField(
        max_length=50,
        help_text="Last name of the contact person"
    )
    email = models.EmailField(
        validators=[EmailValidator()],
        help_text="Email address of the contact person"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Phone number of the contact person"
    )
    job_title = models.CharField(
        max_length=100,
        blank=True,
        help_text="Job title of the contact person"
    )
    
    # Additional information
    company_size = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('1-10', '1-10 employees'),
            ('11-50', '11-50 employees'),
            ('51-200', '51-200 employees'),
            ('201-500', '201-500 employees'),
            ('500+', '500+ employees'),
        ],
        help_text="Size of the company"
    )
    industry = models.CharField(
        max_length=100,
        blank=True,
        help_text="Industry or business sector"
    )
    message = models.TextField(
        blank=True,
        help_text="Additional message or requirements"
    )
    
    # Status and tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the demo request"
    )
    
    # Link to created tenant (when converted)
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Tenant created from this demo request"
    )
    
    # Notes field for workflow tracking
    notes = models.TextField(
        blank=True,
        help_text="Internal notes and status messages"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Admin notes
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes for admin review"
    )
    
    class Meta:
        verbose_name = "Demo Request"
        verbose_name_plural = "Demo Requests"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company_name} - {self.first_name} {self.last_name} ({self.status})"
