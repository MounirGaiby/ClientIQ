"""
Opportunities models for ClientIQ CRM.

This module defines the core models for sales pipeline management:
- SalesStage: Customizable pipeline stages per tenant
- Opportunity: Sales opportunities with stage tracking
- OpportunityHistory: Track stage changes and updates
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from apps.users.models import CustomUser
from apps.contacts.models import Contact, Company


class SalesStage(models.Model):
    """
    Customizable sales pipeline stages for each tenant.
    
    Each tenant can define their own stages with custom names,
    order, and probability values.
    """
    name = models.CharField(
        max_length=100,
        help_text="Stage name (e.g., 'Qualified Lead', 'Proposal Sent')"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Description of what this stage represents"
    )
    
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order of stages (lower numbers first)"
    )
    
    probability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        help_text="Expected close probability for this stage (0-100%)"
    )
    
    is_closed_won = models.BooleanField(
        default=False,
        help_text="Mark as a 'won' stage (deal is closed successfully)"
    )
    
    is_closed_lost = models.BooleanField(
        default=False,
        help_text="Mark as a 'lost' stage (deal is closed unsuccessfully)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this stage is currently active"
    )
    
    # Color for UI display
    color = models.CharField(
        max_length=7,
        default='#6366f1',
        help_text="Hex color code for UI display"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # User tracking
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='stages_created',
        help_text="User who created this stage"
    )

    class Meta:
        verbose_name = "Sales Stage"
        verbose_name_plural = "Sales Stages"
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            # Ensure only one closed won and one closed lost per tenant
            models.UniqueConstraint(
                fields=['is_closed_won'],
                condition=models.Q(is_closed_won=True),
                name='unique_closed_won_stage',
                violation_error_message="Only one 'Closed Won' stage allowed per tenant."
            ),
            models.UniqueConstraint(
                fields=['is_closed_lost'],
                condition=models.Q(is_closed_lost=True),
                name='unique_closed_lost_stage',
                violation_error_message="Only one 'Closed Lost' stage allowed per tenant."
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.probability}%)"

    def save(self, *args, **kwargs):
        # Ensure closed stages have appropriate probabilities
        if self.is_closed_won:
            self.probability = 100
        elif self.is_closed_lost:
            self.probability = 0
        super().save(*args, **kwargs)

    @property
    def is_closed(self):
        """Check if this is a closed stage (won or lost)"""
        return self.is_closed_won or self.is_closed_lost


class Opportunity(models.Model):
    """
    Sales opportunity model representing a potential deal.
    
    Each opportunity is linked to a contact and goes through
    various sales stages until it's won or lost.
    """
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    name = models.CharField(
        max_length=255,
        help_text="Opportunity name/title"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the opportunity"
    )
    
    # Financial information
    value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        help_text="Expected deal value in currency units"
    )
    
    # Relationships
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name='opportunities',
        help_text="Primary contact for this opportunity"
    )
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='opportunities',
        null=True,
        blank=True,
        help_text="Company associated with this opportunity"
    )
    
    stage = models.ForeignKey(
        SalesStage,
        on_delete=models.PROTECT,
        related_name='opportunities',
        help_text="Current sales stage"
    )
    
    # Assignment
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='owned_opportunities',
        help_text="Sales representative assigned to this opportunity"
    )
    
    # Additional fields
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Priority level of this opportunity"
    )
    
    probability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        help_text="Custom probability override (0-100%)"
    )
    
    # Important dates
    expected_close_date = models.DateField(
        null=True,
        blank=True,
        help_text="Expected closing date"
    )
    
    actual_close_date = models.DateField(
        null=True,
        blank=True,
        help_text="Actual closing date (when won/lost)"
    )
    
    # Source tracking
    lead_source = models.CharField(
        max_length=100,
        blank=True,
        help_text="How this opportunity was generated"
    )
    
    # Notes and additional info
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about this opportunity"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # User tracking
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='opportunities_created',
        help_text="User who created this opportunity"
    )
    
    updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='opportunities_updated',
        help_text="User who last updated this opportunity"
    )

    class Meta:
        verbose_name = "Opportunity"
        verbose_name_plural = "Opportunities"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stage']),
            models.Index(fields=['owner']),
            models.Index(fields=['priority']),
            models.Index(fields=['expected_close_date']),
            models.Index(fields=['value']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} - {self.company or self.contact} ({self.stage})"

    def save(self, *args, **kwargs):
        # Auto-set company from contact if not specified
        if not self.company and self.contact.company:
            self.company = self.contact.company
        
        # Use stage probability if custom probability not set
        if self.probability == 0 and self.stage:
            self.probability = self.stage.probability
        
        # Set actual close date for closed stages
        if self.stage and self.stage.is_closed and not self.actual_close_date:
            self.actual_close_date = timezone.now().date()
        
        super().save(*args, **kwargs)

    @property
    def weighted_value(self):
        """Calculate weighted value based on probability"""
        return (self.value * Decimal(str(self.probability))) / Decimal("100")

    @property
    def is_overdue(self):
        """Check if opportunity is past expected close date"""
        if not self.expected_close_date:
            return False
        return (
            self.expected_close_date < timezone.now().date() 
            and not self.stage.is_closed
        )

    @property
    def days_in_stage(self):
        """Calculate days since last stage change"""
        latest_history = self.history.order_by('-created_at').first()
        if latest_history:
            return (timezone.now().date() - latest_history.created_at.date()).days
        return (timezone.now().date() - self.created_at.date()).days

    @property
    def age_days(self):
        """Calculate total age of opportunity in days"""
        return (timezone.now().date() - self.created_at.date()).days

    def move_to_stage(self, new_stage, user=None, notes=None):
        """
        Move opportunity to a new stage with history tracking.
        
        Args:
            new_stage (SalesStage): The stage to move to
            user (CustomUser, optional): User making the change
            notes (str, optional): Notes about the stage change
        """
        old_stage = self.stage
        old_probability = self.probability
        
        self.stage = new_stage
        self.probability = new_stage.probability
        self.updated_by = user
        
        if new_stage.is_closed:
            self.actual_close_date = timezone.now().date()
        
        self.save()
        
        # Create history record
        OpportunityHistory.objects.create(
            opportunity=self,
            old_stage=old_stage,
            new_stage=new_stage,
            old_probability=old_probability,
            new_probability=self.probability,
            changed_by=user,
            notes=notes or f"Moved from {old_stage} to {new_stage}"
        )


class OpportunityHistory(models.Model):
    """
    Track changes to opportunities, especially stage changes.
    
    This model maintains a complete audit trail of all
    opportunity modifications for reporting and analysis.
    """
    
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('stage_changed', 'Stage Changed'),
        ('value_changed', 'Value Changed'),
        ('owner_changed', 'Owner Changed'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
    ]
    
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='history',
        help_text="Opportunity this history entry relates to"
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        default='updated',
        help_text="Type of action that occurred"
    )
    
    # Stage change tracking
    old_stage = models.ForeignKey(
        SalesStage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='history_old_stage',
        help_text="Previous stage (for stage changes)"
    )
    
    new_stage = models.ForeignKey(
        SalesStage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='history_new_stage',
        help_text="New stage (for stage changes)"
    )
    
    # Value change tracking
    old_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Previous opportunity value"
    )
    
    new_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="New opportunity value"
    )
    
    # Probability tracking
    old_probability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Previous probability"
    )
    
    new_probability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="New probability"
    )
    
    # Notes about the change
    notes = models.TextField(
        blank=True,
        help_text="Notes about this change"
    )
    
    # User and timestamp
    changed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        help_text="User who made this change"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Opportunity History"
        verbose_name_plural = "Opportunity Histories"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['opportunity', '-created_at']),
            models.Index(fields=['action']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.opportunity.name} - {self.get_action_display()} at {self.created_at}"