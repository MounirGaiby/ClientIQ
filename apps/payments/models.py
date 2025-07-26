"""
Payment models for handling payment methods, transactions, and billing.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import uuid


class PaymentMethod(models.Model):
    """Model for storing payment method information."""
    
    PAYMENT_TYPES = [
        ('credit_card', 'Credit Card'),
        ('bank_account', 'Bank Account'),
        ('digital_wallet', 'Digital Wallet'),
    ]
    
    CARD_BRANDS = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('amex', 'American Express'),
        ('discover', 'Discover'),
        ('diners', 'Diners Club'),
        ('jcb', 'JCB'),
        ('unknown', 'Unknown'),
    ]
    
    ACCOUNT_TYPES = [
        ('checking', 'Checking'),
        ('savings', 'Savings'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )
    
    # Payment method details
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Credit card fields
    card_last_four = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, choices=CARD_BRANDS, blank=True)
    card_exp_month = models.IntegerField(null=True, blank=True)
    card_exp_year = models.IntegerField(null=True, blank=True)
    
    # Bank account fields
    bank_account_last_four = models.CharField(max_length=4, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, blank=True)
    
    # Billing information
    billing_name = models.CharField(max_length=200, blank=True)
    billing_email = models.EmailField(blank=True)
    billing_address_line1 = models.CharField(max_length=200, blank=True)
    billing_address_line2 = models.CharField(max_length=200, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)
    billing_country = models.CharField(max_length=2, blank=True)  # ISO country code
    
    # External service references
    stripe_payment_method_id = models.CharField(max_length=200, unique=True)
    stripe_customer_id = models.CharField(max_length=200, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_methods'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'is_default']),
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['stripe_payment_method_id']),
        ]
    
    def __str__(self):
        if self.payment_type == 'credit_card':
            return f"{self.tenant.name} - {self.card_brand} ****{self.card_last_four}"
        elif self.payment_type == 'bank_account':
            return f"{self.tenant.name} - {self.bank_name} ****{self.bank_account_last_four}"
        return f"{self.tenant.name} - {self.payment_type}"
    
    def clean(self):
        """Validate payment method data."""
        super().clean()
        
        if self.payment_type == 'credit_card':
            if not self.card_last_four:
                raise ValidationError("Credit card last four digits are required.")
            if not self.card_brand:
                raise ValidationError("Credit card brand is required.")
            if not self.card_exp_month or not self.card_exp_year:
                raise ValidationError("Credit card expiration date is required.")
            if self.card_exp_year < 2020:
                raise ValidationError("Credit card expiration year must be valid.")
        
        elif self.payment_type == 'bank_account':
            if not self.bank_account_last_four:
                raise ValidationError("Bank account last four digits are required.")
            if not self.bank_name:
                raise ValidationError("Bank name is required.")
    
    def save(self, *args, **kwargs):
        # Ensure only one default payment method per tenant
        if self.is_default:
            PaymentMethod.objects.filter(
                tenant=self.tenant,
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if credit card is expired."""
        if self.payment_type != 'credit_card':
            return False
        
        if not self.card_exp_month or not self.card_exp_year:
            return True
        
        now = timezone.now()
        return (
            self.card_exp_year < now.year or
            (self.card_exp_year == now.year and self.card_exp_month < now.month)
        )


class Payment(models.Model):
    """Model for tracking payment transactions."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partial_refund', 'Partially Refunded'),
    ]
    
    CURRENCY_CHOICES = [
        ('usd', 'USD'),
        ('eur', 'EUR'),
        ('gbp', 'GBP'),
        ('cad', 'CAD'),
        ('aud', 'AUD'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    subscription = models.ForeignKey(
        'subscriptions.Subscription',
        on_delete=models.CASCADE,
        related_name='payments',
        null=True,
        blank=True
    )
    payment_method = models.ForeignKey(
        'PaymentMethod',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='usd')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    
    # Refund information
    refunded_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # External service references
    stripe_payment_intent_id = models.CharField(max_length=200, unique=True)
    stripe_charge_id = models.CharField(max_length=200, blank=True)
    
    # Failure information
    failure_reason = models.CharField(max_length=100, blank=True)
    failure_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['subscription']),
            models.Index(fields=['stripe_payment_intent_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.tenant.name} - ${self.amount} - {self.status}"
    
    def clean(self):
        """Validate payment data."""
        super().clean()
        
        if self.amount <= 0:
            raise ValidationError("Payment amount must be positive.")
        
        if self.refunded_amount and self.refunded_amount > self.amount:
            raise ValidationError("Refunded amount cannot exceed payment amount.")
        
        if self.refunded_amount and self.refunded_amount < 0:
            raise ValidationError("Refunded amount cannot be negative.")
    
    def is_successful(self):
        """Check if payment was successful."""
        return self.status == 'succeeded'
    
    def is_failed(self):
        """Check if payment failed."""
        return self.status == 'failed'
    
    def is_pending(self):
        """Check if payment is pending."""
        return self.status in ['pending', 'processing']
    
    def is_refunded(self):
        """Check if payment is refunded."""
        return self.status in ['refunded', 'partial_refund']


class RefundRequest(models.Model):
    """Model for tracking refund requests."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]
    
    REASON_CHOICES = [
        ('customer_request', 'Customer Request'),
        ('duplicate_charge', 'Duplicate Charge'),
        ('service_issue', 'Service Issue'),
        ('billing_error', 'Billing Error'),
        ('fraud', 'Fraud'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(
        'Payment',
        on_delete=models.CASCADE,
        related_name='refund_requests'
    )
    
    # Refund details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    
    # Request information
    requested_by_email = models.EmailField(blank=True)
    requested_by_name = models.CharField(max_length=200, blank=True)
    
    # External service references
    stripe_refund_id = models.CharField(max_length=200, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'refund_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Refund ${self.amount} for {self.payment} - {self.status}"
    
    def clean(self):
        """Validate refund request data."""
        super().clean()
        
        if self.amount <= 0:
            raise ValidationError("Refund amount must be positive.")
        
        if self.amount > self.payment.amount:
            raise ValidationError("Refund amount cannot exceed payment amount.")
        
        # Check if payment has already been refunded
        existing_refunds = RefundRequest.objects.filter(
            payment=self.payment,
            status='processed'
        ).exclude(id=self.id)
        
        total_refunded = sum(refund.amount for refund in existing_refunds)
        if total_refunded + self.amount > self.payment.amount:
            raise ValidationError("Total refund amount would exceed payment amount.")
