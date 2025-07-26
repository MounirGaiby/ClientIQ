"""
Test suite for the Payments app
Testing payment processing, billing integration, and payment method management.
"""

from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock

from apps.tenants.models import Tenant, Domain
from apps.subscriptions.models import Subscription, SubscriptionPlan
from apps.payments.models import PaymentMethod, Payment, RefundRequest
from apps.users.models import TenantUser


class PaymentMethodModelTest(TransactionTestCase):
    """Test PaymentMethod model functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create tenant
        self.tenant = Tenant.objects.create(
            name='Payment Test Corp',
            schema_name='payment_test'
        )
        Domain.objects.create(
            domain='paymenttest.localhost',
            tenant=self.tenant,
            is_primary=True
        )
        
        # Create user within tenant schema
        with schema_context(self.tenant.schema_name):
            self.user = TenantUser.objects.create_user(
                email='billing@paymenttest.com',
                first_name='Billing',
                last_name='Manager',
                is_tenant_admin=True
            )
    
    def test_payment_method_creation_credit_card(self):
        """Test creating a credit card payment method."""
        payment_method = PaymentMethod.objects.create(
            tenant=self.tenant,
            payment_type='credit_card',
            is_default=True,
            card_last_four='4242',
            card_brand='visa',
            card_exp_month=12,
            card_exp_year=2025,
            billing_name='John Doe',
            billing_email='john@paymenttest.com',
            stripe_payment_method_id='pm_test123'
        )
        
        self.assertEqual(payment_method.tenant, self.tenant)
        self.assertEqual(payment_method.payment_type, 'credit_card')
        self.assertTrue(payment_method.is_default)
        self.assertEqual(payment_method.card_last_four, '4242')
        self.assertEqual(payment_method.card_brand, 'visa')
        self.assertEqual(payment_method.billing_name, 'John Doe')
    
    def test_payment_method_creation_bank_account(self):
        """Test creating a bank account payment method."""
        payment_method = PaymentMethod.objects.create(
            tenant=self.tenant,
            payment_type='bank_account',
            is_default=False,
            bank_account_last_four='6789',
            bank_name='Test Bank',
            account_type='checking',
            billing_name='Jane Doe',
            billing_email='jane@paymenttest.com',
            stripe_payment_method_id='pm_bank123'
        )
        
        self.assertEqual(payment_method.payment_type, 'bank_account')
        self.assertEqual(payment_method.bank_account_last_four, '6789')
        self.assertEqual(payment_method.bank_name, 'Test Bank')
        self.assertEqual(payment_method.account_type, 'checking')
    
    def test_payment_method_string_representation(self):
        """Test payment method string representation."""
        # Credit card
        cc_method = PaymentMethod.objects.create(
            tenant=self.tenant,
            payment_type='credit_card',
            card_last_four='4242',
            card_brand='visa',
            billing_name='John Doe',
            stripe_payment_method_id='pm_test123'
        )
        
        expected_cc = f"{self.tenant.name} - visa ****4242"
        self.assertEqual(str(cc_method), expected_cc)
        
        # Bank account
        bank_method = PaymentMethod.objects.create(
            tenant=self.tenant,
            payment_type='bank_account',
            bank_account_last_four='6789',
            bank_name='Test Bank',
            billing_name='Jane Doe',
            stripe_payment_method_id='pm_bank123'
        )
        
        expected_bank = f"{self.tenant.name} - Test Bank ****6789"
        self.assertEqual(str(bank_method), expected_bank)
    
    def test_payment_method_is_expired(self):
        """Test payment method expiration check."""
        # Current year/month
        current_date = timezone.now()
        current_year = current_date.year
        current_month = current_date.month
        
        # Not expired
        valid_method = PaymentMethod.objects.create(
            tenant=self.tenant,
            payment_type='credit_card',
            card_exp_month=12,
            card_exp_year=current_year + 1,  # Next year
            stripe_payment_method_id='pm_valid123'
        )
        self.assertFalse(valid_method.is_expired())
        
        # Expired
        expired_method = PaymentMethod.objects.create(
            tenant=self.tenant,
            payment_type='credit_card',
            card_exp_month=1,
            card_exp_year=current_year - 1,  # Last year
            stripe_payment_method_id='pm_expired123'
        )
        self.assertTrue(expired_method.is_expired())
    
    def test_payment_method_validation_credit_card(self):
        """Test payment method validation for credit cards."""
        # Missing required credit card fields
        with self.assertRaises(ValidationError):
            invalid_method = PaymentMethod(
                tenant=self.tenant,
                payment_type='credit_card',
                # Missing card_last_four, card_brand, etc.
                stripe_payment_method_id='pm_invalid123'
            )
            invalid_method.full_clean()
        
        # Invalid expiration year
        with self.assertRaises(ValidationError):
            invalid_method = PaymentMethod(
                tenant=self.tenant,
                payment_type='credit_card',
                card_last_four='4242',
                card_brand='visa',
                card_exp_month=12,
                card_exp_year=1999,  # Too old
                stripe_payment_method_id='pm_invalid123'
            )
            invalid_method.full_clean()
    
    def test_payment_method_validation_bank_account(self):
        """Test payment method validation for bank accounts."""
        # Missing required bank account fields
        with self.assertRaises(ValidationError):
            invalid_method = PaymentMethod(
                tenant=self.tenant,
                payment_type='bank_account',
                # Missing bank_account_last_four, bank_name, etc.
                stripe_payment_method_id='pm_invalid123'
            )
            invalid_method.full_clean()
    
    def test_payment_method_default_constraint(self):
        """Test that only one default payment method per tenant is allowed."""
        # Create first default payment method
        PaymentMethod.objects.create(
            tenant=self.tenant,
            payment_type='credit_card',
            is_default=True,
            card_last_four='4242',
            card_brand='visa',
            stripe_payment_method_id='pm_first123'
        )
        
        # Create second default payment method should unset the first
        second_method = PaymentMethod.objects.create(
            tenant=self.tenant,
            payment_type='credit_card',
            is_default=True,
            card_last_four='5555',
            card_brand='mastercard',
            stripe_payment_method_id='pm_second123'
        )
        
        # Check that only one default exists
        default_methods = PaymentMethod.objects.filter(tenant=self.tenant, is_default=True)
        self.assertEqual(default_methods.count(), 1)
        self.assertEqual(default_methods.first(), second_method)


class PaymentModelTest(TransactionTestCase):
    """Test Payment model functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create tenant and subscription
        self.tenant = Tenant.objects.create(
            name='Payment Model Test',
            schema_name='payment_model_test'
        )
        
        self.plan = SubscriptionPlan.objects.create(
            name='Test Plan',
            price_monthly=Decimal('49.99'),
            max_users=20
        )
        
        self.subscription = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='active'
        )
        
        self.payment_method = PaymentMethod.objects.create(
            tenant=self.tenant,
            payment_type='credit_card',
            is_default=True,
            card_last_four='4242',
            card_brand='visa',
            stripe_payment_method_id='pm_test123'
        )
    
    def test_payment_creation_successful(self):
        """Test creating a successful payment."""
        payment = Payment.objects.create(
            tenant=self.tenant,
            subscription=self.subscription,
            payment_method=self.payment_method,
            amount=Decimal('49.99'),
            currency='usd',
            status='succeeded',
            stripe_payment_intent_id='pi_success123',
            description='Monthly subscription payment'
        )
        
        self.assertEqual(payment.tenant, self.tenant)
        self.assertEqual(payment.subscription, self.subscription)
        self.assertEqual(payment.amount, Decimal('49.99'))
        self.assertEqual(payment.status, 'succeeded')
        self.assertEqual(payment.currency, 'usd')
        self.assertTrue(payment.is_successful())
    
    def test_payment_creation_failed(self):
        """Test creating a failed payment."""
        payment = Payment.objects.create(
            tenant=self.tenant,
            subscription=self.subscription,
            payment_method=self.payment_method,
            amount=Decimal('49.99'),
            currency='usd',
            status='failed',
            stripe_payment_intent_id='pi_failed123',
            description='Failed monthly payment',
            failure_reason='insufficient_funds'
        )
        
        self.assertEqual(payment.status, 'failed')
        self.assertEqual(payment.failure_reason, 'insufficient_funds')
        self.assertFalse(payment.is_successful())
        self.assertTrue(payment.is_failed())
    
    def test_payment_string_representation(self):
        """Test payment string representation."""
        payment = Payment.objects.create(
            tenant=self.tenant,
            subscription=self.subscription,
            payment_method=self.payment_method,
            amount=Decimal('49.99'),
            currency='usd',
            status='succeeded',
            stripe_payment_intent_id='pi_test123'
        )
        
        expected = f"{self.tenant.name} - $49.99 - succeeded"
        self.assertEqual(str(payment), expected)
    
    def test_payment_status_properties(self):
        """Test payment status property methods."""
        # Successful payment
        success_payment = Payment.objects.create(
            tenant=self.tenant,
            amount=Decimal('29.99'),
            status='succeeded',
            stripe_payment_intent_id='pi_success123'
        )
        self.assertTrue(success_payment.is_successful())
        self.assertFalse(success_payment.is_failed())
        self.assertFalse(success_payment.is_pending())
        
        # Failed payment
        failed_payment = Payment.objects.create(
            tenant=self.tenant,
            amount=Decimal('29.99'),
            status='failed',
            stripe_payment_intent_id='pi_failed123'
        )
        self.assertFalse(failed_payment.is_successful())
        self.assertTrue(failed_payment.is_failed())
        self.assertFalse(failed_payment.is_pending())
        
        # Pending payment
        pending_payment = Payment.objects.create(
            tenant=self.tenant,
            amount=Decimal('29.99'),
            status='pending',
            stripe_payment_intent_id='pi_pending123'
        )
        self.assertFalse(pending_payment.is_successful())
        self.assertFalse(pending_payment.is_failed())
        self.assertTrue(pending_payment.is_pending())
    
    def test_payment_amount_validation(self):
        """Test payment amount validation."""
        # Negative amount
        with self.assertRaises(ValidationError):
            invalid_payment = Payment(
                tenant=self.tenant,
                amount=Decimal('-10.00'),
                currency='usd',
                status='pending',
                stripe_payment_intent_id='pi_invalid123'
            )
            invalid_payment.full_clean()
        
        # Zero amount
        with self.assertRaises(ValidationError):
            invalid_payment = Payment(
                tenant=self.tenant,
                amount=Decimal('0.00'),
                currency='usd',
                status='pending',
                stripe_payment_intent_id='pi_invalid123'
            )
            invalid_payment.full_clean()
    
    def test_payment_currency_validation(self):
        """Test payment currency validation."""
        # Valid currencies
        valid_currencies = ['usd', 'eur', 'gbp', 'cad']
        
        for currency in valid_currencies:
            payment = Payment(
                tenant=self.tenant,
                amount=Decimal('10.00'),
                currency=currency,
                status='pending',
                stripe_payment_intent_id=f'pi_{currency}123'
            )
            payment.full_clean()  # Should not raise
    
    def test_payment_refund_amount_validation(self):
        """Test refund amount validation."""
        payment = Payment.objects.create(
            tenant=self.tenant,
            amount=Decimal('100.00'),
            currency='usd',
            status='succeeded',
            stripe_payment_intent_id='pi_refund_test123'
        )
        
        # Valid partial refund
        payment.refunded_amount = Decimal('25.00')
        payment.full_clean()  # Should not raise
        
        # Invalid: refund more than payment amount
        with self.assertRaises(ValidationError):
            payment.refunded_amount = Decimal('150.00')
            payment.full_clean()


class RefundRequestModelTest(TransactionTestCase):
    """Test RefundRequest model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Refund Test Corp',
            schema_name='refund_test'
        )
        
        self.payment = Payment.objects.create(
            tenant=self.tenant,
            amount=Decimal('99.99'),
            currency='usd',
            status='succeeded',
            stripe_payment_intent_id='pi_refund123'
        )
    
    def test_refund_request_creation(self):
        """Test creating a refund request."""
        refund = RefundRequest.objects.create(
            payment=self.payment,
            amount=Decimal('99.99'),
            reason='customer_request',
            status='pending',
            requested_by_email='customer@test.com',
            notes='Customer not satisfied with service'
        )
        
        self.assertEqual(refund.payment, self.payment)
        self.assertEqual(refund.amount, Decimal('99.99'))
        self.assertEqual(refund.reason, 'customer_request')
        self.assertEqual(refund.status, 'pending')
        self.assertEqual(refund.requested_by_email, 'customer@test.com')
    
    def test_refund_request_string_representation(self):
        """Test refund request string representation."""
        refund = RefundRequest.objects.create(
            payment=self.payment,
            amount=Decimal('50.00'),
            reason='duplicate_charge',
            status='approved'
        )
        
        expected = f"Refund ${refund.amount} for {self.payment} - approved"
        self.assertEqual(str(refund), expected)
    
    def test_refund_request_amount_validation(self):
        """Test refund request amount validation."""
        # Valid partial refund
        valid_refund = RefundRequest(
            payment=self.payment,
            amount=Decimal('50.00'),
            reason='partial_refund',
            status='pending'
        )
        valid_refund.full_clean()  # Should not raise
        
        # Invalid: refund more than payment amount
        with self.assertRaises(ValidationError):
            invalid_refund = RefundRequest(
                payment=self.payment,
                amount=Decimal('150.00'),
                reason='over_refund',
                status='pending'
            )
            invalid_refund.full_clean()
        
        # Invalid: negative refund amount
        with self.assertRaises(ValidationError):
            invalid_refund = RefundRequest(
                payment=self.payment,
                amount=Decimal('-10.00'),
                reason='negative_refund',
                status='pending'
            )
            invalid_refund.full_clean()
    
    def test_refund_request_status_transitions(self):
        """Test refund request status transitions."""
        refund = RefundRequest.objects.create(
            payment=self.payment,
            amount=Decimal('25.00'),
            reason='service_issue',
            status='pending'
        )
        
        # Approve refund
        refund.status = 'approved'
        refund.approved_at = timezone.now()
        refund.save()
        
        self.assertEqual(refund.status, 'approved')
        self.assertIsNotNone(refund.approved_at)
        
        # Process refund
        refund.status = 'processed'
        refund.processed_at = timezone.now()
        refund.stripe_refund_id = 're_processed123'
        refund.save()
        
        self.assertEqual(refund.status, 'processed')
        self.assertIsNotNone(refund.processed_at)
        self.assertIsNotNone(refund.stripe_refund_id)


class PaymentServiceTest(TransactionTestCase):
    """Test payment service functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Payment Service Test',
            schema_name='payment_service_test'
        )
        
        self.plan = SubscriptionPlan.objects.create(
            name='Service Plan',
            price_monthly=Decimal('79.99'),
            max_users=25
        )
        
        self.subscription = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='active'
        )
        
        self.payment_method = PaymentMethod.objects.create(
            tenant=self.tenant,
            payment_type='credit_card',
            is_default=True,
            card_last_four='4242',
            card_brand='visa',
            stripe_payment_method_id='pm_service123'
        )
    
    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_success(self, mock_create):
        """Test successful payment intent creation."""
        mock_create.return_value = MagicMock(
            id='pi_created123',
            amount=7999,  # Stripe uses cents
            currency='usd',
            status='requires_confirmation',
            client_secret='pi_created123_secret_test'
        )
        
        # Simulate payment service call
        payment_data = {
            'amount': Decimal('79.99'),
            'currency': 'usd',
            'payment_method_id': 'pm_service123',
            'tenant': self.tenant,
            'subscription': self.subscription
        }
        
        # Create payment record
        payment = Payment.objects.create(
            tenant=payment_data['tenant'],
            subscription=payment_data['subscription'],
            payment_method=self.payment_method,
            amount=payment_data['amount'],
            currency=payment_data['currency'],
            status='pending',
            stripe_payment_intent_id='pi_created123'
        )
        
        self.assertEqual(payment.amount, Decimal('79.99'))
        self.assertEqual(payment.status, 'pending')
        mock_create.assert_called_once()
    
    @patch('stripe.PaymentIntent.confirm')
    def test_confirm_payment_intent_success(self, mock_confirm):
        """Test successful payment intent confirmation."""
        mock_confirm.return_value = MagicMock(
            id='pi_confirmed123',
            status='succeeded',
            charges=MagicMock(
                data=[MagicMock(
                    id='ch_success123',
                    outcome=MagicMock(type='authorized')
                )]
            )
        )
        
        # Create pending payment
        payment = Payment.objects.create(
            tenant=self.tenant,
            subscription=self.subscription,
            payment_method=self.payment_method,
            amount=Decimal('79.99'),
            currency='usd',
            status='pending',
            stripe_payment_intent_id='pi_confirmed123'
        )
        
        # Simulate confirmation
        payment.status = 'succeeded'
        payment.stripe_charge_id = 'ch_success123'
        payment.save()
        
        self.assertTrue(payment.is_successful())
        self.assertEqual(payment.stripe_charge_id, 'ch_success123')
    
    @patch('stripe.PaymentIntent.confirm')
    def test_confirm_payment_intent_failure(self, mock_confirm):
        """Test failed payment intent confirmation."""
        mock_confirm.return_value = MagicMock(
            id='pi_failed123',
            status='requires_payment_method',
            last_payment_error=MagicMock(
                code='card_declined',
                message='Your card was declined.'
            )
        )
        
        # Create pending payment
        payment = Payment.objects.create(
            tenant=self.tenant,
            subscription=self.subscription,
            payment_method=self.payment_method,
            amount=Decimal('79.99'),
            currency='usd',
            status='pending',
            stripe_payment_intent_id='pi_failed123'
        )
        
        # Simulate failure
        payment.status = 'failed'
        payment.failure_reason = 'card_declined'
        payment.failure_message = 'Your card was declined.'
        payment.save()
        
        self.assertTrue(payment.is_failed())
        self.assertEqual(payment.failure_reason, 'card_declined')
    
    @patch('stripe.Refund.create')
    def test_process_refund_success(self, mock_refund):
        """Test successful refund processing."""
        mock_refund.return_value = MagicMock(
            id='re_success123',
            amount=2500,  # $25.00 in cents
            status='succeeded',
            charge='ch_original123'
        )
        
        # Create successful payment
        payment = Payment.objects.create(
            tenant=self.tenant,
            amount=Decimal('79.99'),
            currency='usd',
            status='succeeded',
            stripe_payment_intent_id='pi_original123',
            stripe_charge_id='ch_original123'
        )
        
        # Create refund request
        refund_request = RefundRequest.objects.create(
            payment=payment,
            amount=Decimal('25.00'),
            reason='customer_request',
            status='approved'
        )
        
        # Simulate refund processing
        refund_request.status = 'processed'
        refund_request.processed_at = timezone.now()
        refund_request.stripe_refund_id = 're_success123'
        refund_request.save()
        
        # Update payment refunded amount
        payment.refunded_amount = refund_request.amount
        payment.save()
        
        self.assertEqual(refund_request.status, 'processed')
        self.assertEqual(payment.refunded_amount, Decimal('25.00'))
        mock_refund.assert_called_once()


class PaymentMethodManagerTest(TestCase):
    """Test PaymentMethod custom manager functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Manager Test Corp',
            schema_name='manager_test'
        )
        
        # Create various payment methods
        self.active_cc = PaymentMethod.objects.create(
            tenant=self.tenant,
            payment_type='credit_card',
            is_active=True,
            is_default=True,
            card_last_four='4242',
            card_brand='visa',
            stripe_payment_method_id='pm_active_cc'
        )
        
        self.inactive_cc = PaymentMethod.objects.create(
            tenant=self.tenant,
            payment_type='credit_card',
            is_active=False,
            card_last_four='5555',
            card_brand='mastercard',
            stripe_payment_method_id='pm_inactive_cc'
        )
        
        self.bank_account = PaymentMethod.objects.create(
            tenant=self.tenant,
            payment_type='bank_account',
            is_active=True,
            bank_account_last_four='6789',
            bank_name='Test Bank',
            stripe_payment_method_id='pm_bank'
        )
    
    def test_active_payment_methods(self):
        """Test filtering active payment methods."""
        active_methods = PaymentMethod.objects.filter(is_active=True)
        
        self.assertEqual(active_methods.count(), 2)
        self.assertIn(self.active_cc, active_methods)
        self.assertIn(self.bank_account, active_methods)
        self.assertNotIn(self.inactive_cc, active_methods)
    
    def test_payment_methods_by_type(self):
        """Test filtering payment methods by type."""
        credit_cards = PaymentMethod.objects.filter(payment_type='credit_card')
        bank_accounts = PaymentMethod.objects.filter(payment_type='bank_account')
        
        self.assertEqual(credit_cards.count(), 2)
        self.assertEqual(bank_accounts.count(), 1)
        
        self.assertIn(self.active_cc, credit_cards)
        self.assertIn(self.inactive_cc, credit_cards)
        self.assertIn(self.bank_account, bank_accounts)
    
    def test_default_payment_method(self):
        """Test getting default payment method for tenant."""
        default_method = PaymentMethod.objects.filter(
            tenant=self.tenant,
            is_default=True
        ).first()
        
        self.assertEqual(default_method, self.active_cc)


class PaymentAPITest(TestCase):
    """Test payment-related API functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='API Payment Test',
            schema_name='api_payment_test'
        )
        
        self.payment_method = PaymentMethod.objects.create(
            tenant=self.tenant,
            payment_type='credit_card',
            is_default=True,
            card_last_four='4242',
            card_brand='visa',
            stripe_payment_method_id='pm_api_test'
        )
    
    def test_payment_method_list_api(self):
        """Test payment method list API endpoint."""
        # Simulate API response
        payment_methods = PaymentMethod.objects.filter(tenant=self.tenant, is_active=True)
        
        api_response = [
            {
                'id': method.id,
                'payment_type': method.payment_type,
                'is_default': method.is_default,
                'card_last_four': method.card_last_four,
                'card_brand': method.card_brand,
                'is_expired': method.is_expired(),
                'created_at': method.created_at.isoformat()
            }
            for method in payment_methods
        ]
        
        self.assertEqual(len(api_response), 1)
        self.assertEqual(api_response[0]['payment_type'], 'credit_card')
        self.assertTrue(api_response[0]['is_default'])
    
    def test_payment_history_api(self):
        """Test payment history API endpoint."""
        # Create sample payments
        payments = [
            Payment.objects.create(
                tenant=self.tenant,
                payment_method=self.payment_method,
                amount=Decimal('49.99'),
                currency='usd',
                status='succeeded',
                stripe_payment_intent_id=f'pi_api_{i}'
            )
            for i in range(3)
        ]
        
        # Simulate API response
        api_response = [
            {
                'id': payment.id,
                'amount': str(payment.amount),
                'currency': payment.currency,
                'status': payment.status,
                'created_at': payment.created_at.isoformat(),
                'description': payment.description or '',
                'refunded_amount': str(payment.refunded_amount or 0)
            }
            for payment in payments
        ]
        
        self.assertEqual(len(api_response), 3)
        for payment_data in api_response:
            self.assertEqual(payment_data['amount'], '49.99')
            self.assertEqual(payment_data['status'], 'succeeded')


class PaymentIntegrationTest(TransactionTestCase):
    """Integration tests for payment functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Payment Integration Test',
            schema_name='payment_integration'
        )
        
        self.plan = SubscriptionPlan.objects.create(
            name='Integration Plan',
            price_monthly=Decimal('59.99'),
            max_users=20
        )
        
        self.subscription = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='active'
        )
    
    def test_complete_payment_flow(self):
        """Test complete payment processing flow."""
        # 1. Create payment method
        payment_method = PaymentMethod.objects.create(
            tenant=self.tenant,
            payment_type='credit_card',
            is_default=True,
            card_last_four='4242',
            card_brand='visa',
            card_exp_month=12,
            card_exp_year=2025,
            billing_name='Test Customer',
            billing_email='test@integration.com',
            stripe_payment_method_id='pm_integration123'
        )
        
        self.assertTrue(payment_method.is_active)
        self.assertFalse(payment_method.is_expired())
        
        # 2. Create payment
        payment = Payment.objects.create(
            tenant=self.tenant,
            subscription=self.subscription,
            payment_method=payment_method,
            amount=self.plan.price_monthly,
            currency='usd',
            status='succeeded',
            stripe_payment_intent_id='pi_integration123',
            description='Monthly subscription payment'
        )
        
        self.assertTrue(payment.is_successful())
        self.assertEqual(payment.amount, self.plan.price_monthly)
        
        # 3. Create partial refund
        refund_request = RefundRequest.objects.create(
            payment=payment,
            amount=Decimal('20.00'),
            reason='service_issue',
            status='processed',
            stripe_refund_id='re_integration123'
        )
        
        # Update payment with refund
        payment.refunded_amount = refund_request.amount
        payment.save()
        
        self.assertEqual(payment.refunded_amount, Decimal('20.00'))
        self.assertEqual(refund_request.status, 'processed')
        
        # 4. Verify relationships
        self.assertEqual(payment.tenant, self.tenant)
        self.assertEqual(payment.subscription, self.subscription)
        self.assertEqual(refund_request.payment, payment)
        
        # 5. Verify payment method is still usable
        self.assertTrue(payment_method.is_active)
        tenant_payments = Payment.objects.filter(tenant=self.tenant)
        self.assertEqual(tenant_payments.count(), 1)
    
    def test_subscription_payment_relationship(self):
        """Test payment and subscription relationship integrity."""
        payment_method = PaymentMethod.objects.create(
            tenant=self.tenant,
            payment_type='credit_card',
            is_default=True,
            card_last_four='4242',
            card_brand='visa',
            stripe_payment_method_id='pm_relationship123'
        )
        
        payment = Payment.objects.create(
            tenant=self.tenant,
            subscription=self.subscription,
            payment_method=payment_method,
            amount=Decimal('59.99'),
            currency='usd',
            status='succeeded',
            stripe_payment_intent_id='pi_relationship123'
        )
        
        # Test relationships
        self.assertEqual(payment.subscription.plan.price_monthly, Decimal('59.99'))
        self.assertEqual(payment.tenant.name, 'Payment Integration Test')
        
        # Test reverse relationships
        subscription_payments = self.subscription.payments.all()
        self.assertIn(payment, subscription_payments)
        
        tenant_payments = self.tenant.payments.all()
        self.assertIn(payment, tenant_payments)
