"""
Contacts models for ClientIQ CRM.

This module defines the core models for contact management:
- Company: Organization/company information
- Contact: Individual contact details with relationship to companies
- ContactType: Enumeration for contact classification
"""

from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.utils import timezone
from apps.users.models import CustomUser


class ContactType(models.TextChoices):
    """Contact type classification"""
    PROSPECT = 'prospect', 'Prospect'
    CLIENT = 'client', 'Client'
    PARTNER = 'partner', 'Partner'


class Company(models.Model):
    """
    Company/Organization model for tenant isolation.
    
    Each company belongs to a tenant and can have multiple contacts.
    """
    name = models.CharField(
        max_length=255,
        help_text="Company name"
    )
    
    website = models.URLField(
        blank=True,
        help_text="Company website URL"
    )
    
    industry = models.CharField(
        max_length=100,
        blank=True,
        help_text="Industry sector"
    )
    
    size = models.CharField(
        max_length=50,
        blank=True,
        help_text="Company size (e.g., '1-10', '11-50', '51-200', '200+')"
    )
    
    # Address information
    address_line1 = models.CharField(
        max_length=255,
        blank=True,
        help_text="Street address"
    )
    
    address_line2 = models.CharField(
        max_length=255,
        blank=True,
        help_text="Additional address information"
    )
    
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text="City"
    )
    
    state = models.CharField(
        max_length=100,
        blank=True,
        help_text="State or province"
    )
    
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="Postal or ZIP code"
    )
    
    country = models.CharField(
        max_length=100,
        blank=True,
        help_text="Country"
    )
    
    # Phone validation for international numbers
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    phone = models.CharField(
        validators=[phone_validator],
        max_length=17,
        blank=True,
        help_text="Main company phone number"
    )
    
    # Notes and metadata
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about the company"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the company was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the company was last updated"
    )
    
    # User who created/modified
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='companies_created',
        help_text="User who created this company"
    )
    
    updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='companies_updated',
        help_text="User who last updated this company"
    )

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['industry']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name

    @property
    def full_address(self):
        """Return formatted full address"""
        address_parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join(part for part in address_parts if part)


class Contact(models.Model):
    """
    Contact model for individual contact management.
    
    Each contact is tenant-isolated and can be associated with a company.
    Includes scoring system for lead qualification.
    """
    
    # Basic contact information
    first_name = models.CharField(
        max_length=100,
        help_text="Contact's first name"
    )
    
    last_name = models.CharField(
        max_length=100,
        help_text="Contact's last name"
    )
    
    email = models.EmailField(
        validators=[EmailValidator()],
        help_text="Primary email address"
    )
    
    # Phone validation
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    phone = models.CharField(
        validators=[phone_validator],
        max_length=17,
        blank=True,
        help_text="Primary phone number"
    )
    
    # Professional information
    job_title = models.CharField(
        max_length=150,
        blank=True,
        help_text="Job title or position"
    )
    
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contacts',
        help_text="Associated company"
    )
    
    # Contact classification
    contact_type = models.CharField(
        max_length=20,
        choices=ContactType.choices,
        default=ContactType.PROSPECT,
        help_text="Contact type classification"
    )
    
    # Lead scoring (0-100)
    score = models.IntegerField(
        default=0,
        help_text="Lead score (0-100) for qualification"
    )
    
    # Additional contact information
    linkedin_url = models.URLField(
        blank=True,
        help_text="LinkedIn profile URL"
    )
    
    # Notes and status
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about the contact"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the contact is active"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the contact was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the contact was last updated"
    )
    
    # User tracking
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='contacts_created',
        help_text="User who created this contact"
    )
    
    updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='contacts_updated',
        help_text="User who last updated this contact"
    )
    
    # Tenant owner (for additional security)
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='owned_contacts',
        null=True,
        blank=True,
        help_text="User who owns this contact"
    )

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['email']),
            models.Index(fields=['contact_type']),
            models.Index(fields=['score']),
            models.Index(fields=['created_at']),
            models.Index(fields=['owner']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['email'],
                name='unique_contact_email_per_tenant'
            )
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def company_name(self):
        """Return company name or empty string"""
        return self.company.name if self.company else ""

    def update_score(self, points):
        """Update contact score with bounds checking"""
        self.score = max(0, min(100, self.score + points))
        self.save(update_fields=['score', 'updated_at'])
    
    def get_score_level(self):
        """Return score level classification"""
        if self.score >= 80:
            return "Hot"
        elif self.score >= 60:
            return "Warm" 
        elif self.score >= 40:
            return "Cold"
        else:
            return "Unqualified"


class ContactTag(models.Model):
    """
    Tags for contact categorization and segmentation.
    """
    name = models.CharField(
        max_length=50,
        help_text="Tag name"
    )
    
    color = models.CharField(
        max_length=7,
        default="#3B82F6",
        help_text="Hex color code for tag display"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='contact_tags_created'
    )

    class Meta:
        verbose_name = "Contact Tag"
        verbose_name_plural = "Contact Tags"
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                name='unique_tag_name_per_tenant'
            )
        ]

    def __str__(self):
        return self.name


class ContactTagAssignment(models.Model):
    """
    Many-to-many relationship between contacts and tags.
    """
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name='tag_assignments',
        null=True,
        default=None
    )
    
    tag = models.ForeignKey(
        ContactTag,
        on_delete=models.CASCADE,
        related_name='contact_assignments',
        null=True,
        default=None
    )
    
    assigned_at = models.DateTimeField(
        auto_now_add=True
    )
    
    assigned_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='tag_assignments_made'
    )

    class Meta:
        verbose_name = "Contact Tag Assignment"
        verbose_name_plural = "Contact Tag Assignments"
        constraints = [
            models.UniqueConstraint(
                fields=['contact', 'tag'],
                name='unique_contact_tag_assignment'
            )
        ]

    def __str__(self):
        return f"{self.contact} - {self.tag}"
