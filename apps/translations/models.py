"""
Translation models for multi-language support.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


class Language(models.Model):
    """Model for supported languages."""
    
    code = models.CharField(max_length=10, unique=True)  # ISO 639-1/639-2 code
    name = models.CharField(max_length=100)  # English name
    native_name = models.CharField(max_length=100)  # Native name
    is_active = models.BooleanField(default=True)
    is_rtl = models.BooleanField(default=False)  # Right-to-left script
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'languages'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class TranslationKey(models.Model):
    """Model for translation keys."""
    
    CONTEXT_CHOICES = [
        ('user_interface', 'User Interface'),
        ('email_templates', 'Email Templates'),
        ('error_messages', 'Error Messages'),
        ('notifications', 'Notifications'),
        ('help_text', 'Help Text'),
        ('api_responses', 'API Responses'),
        ('other', 'Other'),
    ]
    
    key = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    context = models.CharField(max_length=50, choices=CONTEXT_CHOICES, default='other')
    default_value = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'translation_keys'
        ordering = ['key']
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['context']),
        ]
    
    def __str__(self):
        return self.key


class Translation(models.Model):
    """Model for translations."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='translations'
    )
    translation_key = models.ForeignKey(
        'TranslationKey',
        on_delete=models.CASCADE,
        related_name='translations'
    )
    language = models.ForeignKey(
        'Language',
        on_delete=models.CASCADE,
        related_name='translations'
    )
    value = models.TextField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'translations'
        unique_together = ['tenant', 'translation_key', 'language']
        ordering = ['translation_key__key', 'language__code']
        indexes = [
            models.Index(fields=['tenant', 'translation_key', 'language']),
            models.Index(fields=['translation_key', 'language']),
            models.Index(fields=['tenant', 'language']),
        ]
    
    def __str__(self):
        return f"{self.tenant.name} - {self.translation_key.key} ({self.language.code})"
