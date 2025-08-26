"""
Activities models for ClientIQ CRM.

This module defines models for task management, interaction tracking,
and follow-up activities in the CRM system.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import datetime, timedelta
from apps.users.models import CustomUser
from apps.contacts.models import Contact, Company
from apps.opportunities.models import Opportunity


class ActivityType(models.Model):
    """
    Types of activities that can be performed.
    
    Examples: Call, Email, Meeting, Task, Note, etc.
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Activity type name (e.g., 'Call', 'Email', 'Meeting')"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Description of this activity type"
    )
    
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icon name for UI display"
    )
    
    color = models.CharField(
        max_length=7,
        default='#6366f1',
        help_text="Hex color code for UI display"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this activity type is available for use"
    )
    
    requires_duration = models.BooleanField(
        default=False,
        help_text="Whether activities of this type require a duration"
    )
    
    requires_outcome = models.BooleanField(
        default=False,
        help_text="Whether activities of this type require an outcome"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Activity Type"
        verbose_name_plural = "Activity Types"
        ordering = ['name']

    def __str__(self):
        return self.name


class Activity(models.Model):
    """
    Core activity model for tracking interactions, tasks, and follow-ups.
    
    Can be linked to contacts, companies, or opportunities.
    """
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('overdue', 'Overdue'),
    ]
    
    OUTCOME_CHOICES = [
        ('successful', 'Successful'),
        ('unsuccessful', 'Unsuccessful'),
        ('no_answer', 'No Answer'),
        ('callback_requested', 'Callback Requested'),
        ('meeting_scheduled', 'Meeting Scheduled'),
        ('follow_up_needed', 'Follow-up Needed'),
        ('not_interested', 'Not Interested'),
        ('other', 'Other'),
    ]

    # Basic Information
    title = models.CharField(
        max_length=200,
        help_text="Activity title or subject"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the activity"
    )
    
    activity_type = models.ForeignKey(
        ActivityType,
        on_delete=models.PROTECT,
        related_name='activities',
        help_text="Type of activity"
    )
    
    # Scheduling
    scheduled_at = models.DateTimeField(
        help_text="When this activity is scheduled to occur"
    )
    
    duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(1440)],  # Max 24 hours
        help_text="Duration in minutes"
    )
    
    # Status and Priority
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    
    # Relationships
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name='activities',
        null=True,
        blank=True,
        help_text="Related contact"
    )
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='activities',
        null=True,
        blank=True,
        help_text="Related company"
    )
    
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='activities',
        null=True,
        blank=True,
        help_text="Related opportunity"
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='assigned_activities',
        help_text="User responsible for this activity"
    )
    
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_activities',
        help_text="User who created this activity"
    )
    
    # Completion Details
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this activity was completed"
    )
    
    outcome = models.CharField(
        max_length=20,
        choices=OUTCOME_CHOICES,
        blank=True,
        help_text="Outcome of the activity"
    )
    
    outcome_notes = models.TextField(
        blank=True,
        help_text="Additional notes about the outcome"
    )
    
    # Reminders
    reminder_minutes_before = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Minutes before activity to send reminder (null = no reminder)"
    )
    
    reminder_sent = models.BooleanField(
        default=False,
        help_text="Whether reminder has been sent"
    )
    
    # Follow-up
    requires_follow_up = models.BooleanField(
        default=False,
        help_text="Whether this activity requires a follow-up"
    )
    
    follow_up_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When to follow up on this activity"
    )
    
    parent_activity = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='follow_up_activities',
        help_text="Parent activity if this is a follow-up"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"
        ordering = ['-scheduled_at']
        indexes = [
            models.Index(fields=['scheduled_at']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['contact']),
            models.Index(fields=['company']),
            models.Index(fields=['opportunity']),
            models.Index(fields=['status', 'scheduled_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        """Override save to handle status changes and completion."""
        # Auto-set completed_at when status changes to completed
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        
        # Auto-set overdue status for past scheduled activities
        if (self.scheduled_at < timezone.now() and 
            self.status == 'scheduled'):
            self.status = 'overdue'
        
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Check if activity is overdue."""
        return (self.scheduled_at < timezone.now() and 
                self.status in ['scheduled', 'in_progress'])

    @property
    def end_time(self):
        """Calculate end time based on duration."""
        if self.duration_minutes:
            return self.scheduled_at + timedelta(minutes=self.duration_minutes)
        return self.scheduled_at

    @property
    def reminder_time(self):
        """Calculate when reminder should be sent."""
        if self.reminder_minutes_before:
            return self.scheduled_at - timedelta(minutes=self.reminder_minutes_before)
        return None

    def mark_completed(self, outcome=None, outcome_notes='', user=None):
        """Mark activity as completed with optional outcome."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if outcome:
            self.outcome = outcome
        if outcome_notes:
            self.outcome_notes = outcome_notes
        self.save()
        
        # Create follow-up activity if required
        if self.requires_follow_up and self.follow_up_date:
            self.create_follow_up_activity(user or self.assigned_to)

    def create_follow_up_activity(self, user):
        """Create a follow-up activity."""
        follow_up = Activity.objects.create(
            title=f"Follow-up: {self.title}",
            description=f"Follow-up for: {self.description}",
            activity_type=self.activity_type,
            scheduled_at=self.follow_up_date,
            priority=self.priority,
            contact=self.contact,
            company=self.company,
            opportunity=self.opportunity,
            assigned_to=self.assigned_to,
            created_by=user,
            parent_activity=self
        )
        return follow_up


class Task(models.Model):
    """
    Simple task model for to-do items and personal tasks.
    
    Different from Activity - tasks are more personal/internal
    while activities are client-facing interactions.
    """
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(
        max_length=200,
        help_text="Task title"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Task description"
    )
    
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='todo'
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    
    # Due date
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this task is due"
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text="User responsible for this task"
    )
    
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks',
        help_text="User who created this task"
    )
    
    # Optional relationships
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True,
        help_text="Related contact"
    )
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True,
        help_text="Related company"
    )
    
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True,
        help_text="Related opportunity"
    )
    
    # Completion
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this task was completed"
    )
    
    completion_notes = models.TextField(
        blank=True,
        help_text="Notes about task completion"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['priority', 'due_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    @property
    def is_overdue(self):
        """Check if task is overdue."""
        return (self.due_date and 
                self.due_date < timezone.now() and 
                self.status != 'completed')

    def mark_completed(self, notes=''):
        """Mark task as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if notes:
            self.completion_notes = notes
        self.save()


class InteractionLog(models.Model):
    """
    Log of all interactions with contacts/companies.
    
    This is automatically created when activities are completed
    and can also be manually created for ad-hoc interactions.
    """
    
    INTERACTION_TYPES = [
        ('call_inbound', 'Inbound Call'),
        ('call_outbound', 'Outbound Call'),
        ('email_sent', 'Email Sent'),
        ('email_received', 'Email Received'),
        ('meeting', 'Meeting'),
        ('note', 'Note'),
        ('sms', 'SMS'),
        ('other', 'Other'),
    ]

    # Basic Information
    title = models.CharField(
        max_length=200,
        help_text="Interaction title"
    )
    
    interaction_type = models.CharField(
        max_length=20,
        choices=INTERACTION_TYPES,
        help_text="Type of interaction"
    )
    
    notes = models.TextField(
        help_text="Detailed notes about the interaction"
    )
    
    # Timing
    interaction_date = models.DateTimeField(
        default=timezone.now,
        help_text="When the interaction occurred"
    )
    
    duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Duration of interaction in minutes"
    )
    
    # Relationships
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name='interactions',
        null=True,
        blank=True,
        help_text="Related contact"
    )
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='interactions',
        null=True,
        blank=True,
        help_text="Related company"
    )
    
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='interactions',
        null=True,
        blank=True,
        help_text="Related opportunity"
    )
    
    # User who logged the interaction
    logged_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='logged_interactions',
        help_text="User who logged this interaction"
    )
    
    # Optional: Link to the activity that generated this log
    source_activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='interaction_logs',
        null=True,
        blank=True,
        help_text="Activity that generated this interaction log"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Interaction Log"
        verbose_name_plural = "Interaction Logs"
        ordering = ['-interaction_date']
        indexes = [
            models.Index(fields=['contact', 'interaction_date']),
            models.Index(fields=['company', 'interaction_date']),
            models.Index(fields=['opportunity', 'interaction_date']),
            models.Index(fields=['logged_by', 'interaction_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.interaction_date.strftime('%Y-%m-%d %H:%M')}"


class FollowUpRule(models.Model):
    """
    Rules for automated follow-up creation.
    
    Defines when and what type of follow-ups should be automatically
    created based on activity outcomes.
    """
    
    name = models.CharField(
        max_length=100,
        help_text="Name of this follow-up rule"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Description of when this rule applies"
    )
    
    # Trigger conditions
    trigger_activity_type = models.ForeignKey(
        ActivityType,
        on_delete=models.CASCADE,
        related_name='follow_up_rules',
        help_text="Activity type that triggers this rule"
    )
    
    trigger_outcome = models.CharField(
        max_length=20,
        choices=Activity.OUTCOME_CHOICES,
        help_text="Activity outcome that triggers this rule"
    )
    
    # Follow-up creation
    follow_up_activity_type = models.ForeignKey(
        ActivityType,
        on_delete=models.CASCADE,
        related_name='auto_follow_up_rules',
        help_text="Type of follow-up activity to create"
    )
    
    follow_up_delay_days = models.PositiveIntegerField(
        default=1,
        help_text="Days to wait before follow-up"
    )
    
    follow_up_title_template = models.CharField(
        max_length=200,
        help_text="Template for follow-up activity title (use {original_title})"
    )
    
    follow_up_description_template = models.TextField(
        help_text="Template for follow-up description"
    )
    
    # Configuration
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this rule is active"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Follow-up Rule"
        verbose_name_plural = "Follow-up Rules"
        ordering = ['name']

    def __str__(self):
        return self.name

    def create_follow_up(self, source_activity):
        """Create a follow-up activity based on this rule."""
        follow_up_date = timezone.now() + timedelta(days=self.follow_up_delay_days)
        
        title = self.follow_up_title_template.format(
            original_title=source_activity.title
        )
        
        description = self.follow_up_description_template.format(
            original_title=source_activity.title,
            original_description=source_activity.description,
            outcome=source_activity.get_outcome_display()
        )
        
        follow_up = Activity.objects.create(
            title=title,
            description=description,
            activity_type=self.follow_up_activity_type,
            scheduled_at=follow_up_date,
            priority=source_activity.priority,
            contact=source_activity.contact,
            company=source_activity.company,
            opportunity=source_activity.opportunity,
            assigned_to=source_activity.assigned_to,
            created_by=source_activity.assigned_to,  # Auto-created
            parent_activity=source_activity
        )
        
        return follow_up