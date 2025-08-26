"""
Signal handlers for activities app.

Handles automatic interaction logging, follow-up creation,
and reminder management.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta

from .models import Activity, Task, InteractionLog, FollowUpRule


@receiver(post_save, sender=Activity)
def handle_activity_completion(sender, instance, created, **kwargs):
    """
    Handle activity completion by creating interaction logs
    and triggering follow-up rules.
    """
    if not created and instance.status == 'completed':
        # Create interaction log if linked to contact/company
        if instance.contact or instance.company:
            # Check if interaction log already exists for this activity
            existing_log = InteractionLog.objects.filter(
                source_activity=instance
            ).exists()
            
            if not existing_log:
                # Map activity type to interaction type
                interaction_type_mapping = {
                    'Call': 'call_outbound',
                    'Email': 'email_sent',
                    'Meeting': 'meeting',
                    'Task': 'other',
                    'Note': 'note'
                }
                
                interaction_type = interaction_type_mapping.get(
                    instance.activity_type.name,
                    'other'
                )
                
                InteractionLog.objects.create(
                    title=f"Completed: {instance.title}",
                    interaction_type=interaction_type,
                    notes=f"Activity completed. Outcome: {instance.get_outcome_display()}. Notes: {instance.outcome_notes}",
                    interaction_date=instance.completed_at or timezone.now(),
                    duration_minutes=instance.duration_minutes,
                    contact=instance.contact,
                    company=instance.company,
                    opportunity=instance.opportunity,
                    logged_by=instance.assigned_to,
                    source_activity=instance
                )
        
        # Apply automatic follow-up rules
        apply_follow_up_rules(instance)


@receiver(pre_save, sender=Activity)
def handle_activity_status_change(sender, instance, **kwargs):
    """
    Handle activity status changes to update overdue status
    and set completion timestamp.
    """
    if instance.pk:
        try:
            old_instance = Activity.objects.get(pk=instance.pk)
            
            # If status changed to completed, set completed_at
            if (old_instance.status != 'completed' and 
                instance.status == 'completed' and 
                not instance.completed_at):
                instance.completed_at = timezone.now()
            
            # Check for overdue status
            if (instance.scheduled_at < timezone.now() and 
                instance.status == 'scheduled'):
                instance.status = 'overdue'
                
        except Activity.DoesNotExist:
            pass


@receiver(post_save, sender=Task)
def handle_task_completion(sender, instance, created, **kwargs):
    """
    Handle task completion and create interaction logs if needed.
    """
    if not created and instance.status == 'completed':
        # Create interaction log if task is related to contact/company
        if instance.contact or instance.company:
            InteractionLog.objects.get_or_create(
                title=f"Task Completed: {instance.title}",
                interaction_type='other',
                notes=f"Task completed. Notes: {instance.completion_notes}",
                interaction_date=instance.completed_at or timezone.now(),
                contact=instance.contact,
                company=instance.company,
                opportunity=instance.opportunity,
                logged_by=instance.assigned_to,
                defaults={}
            )


def apply_follow_up_rules(activity):
    """
    Apply automatic follow-up rules for a completed activity.
    """
    if not activity.outcome:
        return
    
    # Find matching follow-up rules
    rules = FollowUpRule.objects.filter(
        is_active=True,
        trigger_activity_type=activity.activity_type,
        trigger_outcome=activity.outcome
    )
    
    for rule in rules:
        try:
            rule.create_follow_up(activity)
        except Exception as e:
            # Log error but don't break the process
            print(f"Error creating follow-up for rule {rule.name}: {e}")


# Reminder System (could be moved to a separate service)

def send_activity_reminders():
    """
    Send reminders for upcoming activities.
    
    This function should be called by a scheduled task/cron job.
    """
    now = timezone.now()
    
    # Find activities that need reminders
    activities_needing_reminders = Activity.objects.filter(
        reminder_minutes_before__isnull=False,
        reminder_sent=False,
        status='scheduled'
    )
    
    for activity in activities_needing_reminders:
        reminder_time = activity.reminder_time
        
        if reminder_time and reminder_time <= now:
            send_activity_reminder(activity)
            activity.reminder_sent = True
            activity.save(update_fields=['reminder_sent'])


def send_activity_reminder(activity):
    """
    Send reminder email for an activity.
    
    In a real implementation, you might want to use:
    - Celery for background tasks
    - More sophisticated notification system
    - SMS, push notifications, etc.
    """
    try:
        subject = f"Reminder: {activity.title}"
        message = f"""
        Hello {activity.assigned_to.get_full_name()},
        
        This is a reminder for your upcoming activity:
        
        Title: {activity.title}
        Type: {activity.activity_type.name}
        Scheduled: {activity.scheduled_at.strftime('%Y-%m-%d %H:%M')}
        
        {f'Contact: {activity.contact.get_full_name()}' if activity.contact else ''}
        {f'Company: {activity.company.name}' if activity.company else ''}
        {f'Opportunity: {activity.opportunity.name}' if activity.opportunity else ''}
        
        Description:
        {activity.description}
        
        Best regards,
        ClientIQ System
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@clientiq.com'),
            recipient_list=[activity.assigned_to.email],
            fail_silently=True
        )
        
    except Exception as e:
        print(f"Error sending reminder for activity {activity.id}: {e}")


# Utility functions for management commands

def create_default_activity_types():
    """Create default activity types for a tenant."""
    default_types = [
        {
            'name': 'Call',
            'description': 'Phone call with contact',
            'icon': 'phone',
            'color': '#10B981',
            'requires_duration': True,
            'requires_outcome': True
        },
        {
            'name': 'Email',
            'description': 'Email communication',
            'icon': 'mail',
            'color': '#3B82F6',
            'requires_duration': False,
            'requires_outcome': True
        },
        {
            'name': 'Meeting',
            'description': 'In-person or virtual meeting',
            'icon': 'calendar',
            'color': '#8B5CF6',
            'requires_duration': True,
            'requires_outcome': True
        },
        {
            'name': 'Task',
            'description': 'General task or follow-up',
            'icon': 'check-square',
            'color': '#F59E0B',
            'requires_duration': False,
            'requires_outcome': False
        },
        {
            'name': 'Note',
            'description': 'Add a note or comment',
            'icon': 'edit',
            'color': '#6B7280',
            'requires_duration': False,
            'requires_outcome': False
        }
    ]
    
    created_types = []
    from .models import ActivityType
    
    for type_data in default_types:
        activity_type, created = ActivityType.objects.get_or_create(
            name=type_data['name'],
            defaults=type_data
        )
        if created:
            created_types.append(activity_type)
    
    return created_types


def create_default_follow_up_rules():
    """Create default follow-up rules for a tenant."""
    from .models import ActivityType
    
    try:
        call_type = ActivityType.objects.get(name='Call')
        email_type = ActivityType.objects.get(name='Email')
        
        default_rules = [
            {
                'name': 'Follow-up after no answer call',
                'description': 'Create email follow-up when call gets no answer',
                'trigger_activity_type': call_type,
                'trigger_outcome': 'no_answer',
                'follow_up_activity_type': email_type,
                'follow_up_delay_days': 1,
                'follow_up_title_template': 'Follow-up email after call: {original_title}',
                'follow_up_description_template': 'Follow-up email after unsuccessful call attempt. Original call: {original_title}'
            },
            {
                'name': 'Call follow-up for callback requests',
                'description': 'Schedule callback when requested',
                'trigger_activity_type': call_type,
                'trigger_outcome': 'callback_requested',
                'follow_up_activity_type': call_type,
                'follow_up_delay_days': 1,
                'follow_up_title_template': 'Callback: {original_title}',
                'follow_up_description_template': 'Scheduled callback as requested. Original call: {original_title}'
            }
        ]
        
        created_rules = []
        for rule_data in default_rules:
            rule, created = FollowUpRule.objects.get_or_create(
                name=rule_data['name'],
                defaults=rule_data
            )
            if created:
                created_rules.append(rule)
        
        return created_rules
        
    except ActivityType.DoesNotExist:
        print("Activity types not found. Create activity types first.")
        return []