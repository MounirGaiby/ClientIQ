"""
Test suite for the Subscriptions app
Testing subscription models, billing cycles, and subscription management functionality.
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
from apps.subscriptions.models import Subscription, SubscriptionPlan, BillingHistory
from apps.users.models import TenantUser


class SubscriptionPlanModelTest(TestCase):
    """Test SubscriptionPlan model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.plan_data = {
            'name': 'Professional Plan',
            'description': 'Professional tier with advanced features',
            'price_monthly': Decimal('99.99'),
            'price_yearly': Decimal('999.99'),
            'max_users': 50,
            'max_storage_gb': 100,
            'features': {
                'api_access': True,
                'advanced_analytics': True,
                'priority_support': True,
                'custom_integrations': False
            },
            'is_active': True
        }
    
    def test_subscription_plan_creation(self):
        """Test creating a subscription plan."""
        plan = SubscriptionPlan.objects.create(**self.plan_data)
        
        self.assertEqual(plan.name, 'Professional Plan')
        self.assertEqual(plan.price_monthly, Decimal('99.99'))
        self.assertEqual(plan.price_yearly, Decimal('999.99'))
        self.assertEqual(plan.max_users, 50)
        self.assertTrue(plan.features['api_access'])
        self.assertTrue(plan.is_active)
    
    def test_subscription_plan_string_representation(self):
        """Test subscription plan string representation."""
        plan = SubscriptionPlan.objects.create(**self.plan_data)
        self.assertEqual(str(plan), 'Professional Plan')
    
    def test_subscription_plan_price_validation(self):
        """Test subscription plan price validation."""
        # Test negative price
        invalid_data = self.plan_data.copy()
        invalid_data['price_monthly'] = Decimal('-10.00')
        
        plan = SubscriptionPlan(**invalid_data)
        with self.assertRaises(ValidationError):
            plan.full_clean()
    
    def test_subscription_plan_max_users_validation(self):
        """Test max users validation."""
        # Test negative max users
        invalid_data = self.plan_data.copy()
        invalid_data['max_users'] = -5
        
        plan = SubscriptionPlan(**invalid_data)
        with self.assertRaises(ValidationError):
            plan.full_clean()
        
        # Test zero max users (should be valid for unlimited)
        valid_data = self.plan_data.copy()
        valid_data['max_users'] = 0
        
        plan = SubscriptionPlan(**valid_data)
        plan.full_clean()  # Should not raise
    
    def test_subscription_plan_yearly_discount_calculation(self):
        """Test yearly discount calculation."""
        plan = SubscriptionPlan.objects.create(**self.plan_data)
        
        monthly_yearly_total = plan.price_monthly * 12
        yearly_discount = monthly_yearly_total - plan.price_yearly
        discount_percentage = (yearly_discount / monthly_yearly_total) * 100
        
        self.assertGreater(yearly_discount, 0)
        self.assertAlmostEqual(discount_percentage, 16.67, places=1)  # ~17% discount
    
    def test_subscription_plan_features_json_field(self):
        """Test features JSON field functionality."""
        plan = SubscriptionPlan.objects.create(**self.plan_data)
        
        # Test feature access
        self.assertTrue(plan.features['api_access'])
        self.assertFalse(plan.features['custom_integrations'])
        
        # Test feature modification
        plan.features['custom_integrations'] = True
        plan.features['new_feature'] = 'beta'
        plan.save()
        
        # Reload and verify
        plan.refresh_from_db()
        self.assertTrue(plan.features['custom_integrations'])
        self.assertEqual(plan.features['new_feature'], 'beta')


class SubscriptionModelTest(TransactionTestCase):
    """Test Subscription model functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create tenant
        self.tenant = Tenant.objects.create(
            name='Subscription Test Corp',
            schema_name='sub_test'
        )
        Domain.objects.create(
            domain='subtest.localhost',
            tenant=self.tenant,
            is_primary=True
        )
        
        # Create subscription plan
        self.plan = SubscriptionPlan.objects.create(
            name='Test Plan',
            description='Test subscription plan',
            price_monthly=Decimal('49.99'),
            price_yearly=Decimal('499.99'),
            max_users=25,
            max_storage_gb=50,
            features={'api_access': True},
            is_active=True
        )
        
        # Create user within tenant schema
        with schema_context(self.tenant.schema_name):
            self.user = TenantUser.objects.create_user(
                email='admin@subtest.com',
                first_name='Admin',
                last_name='User',
                is_tenant_admin=True
            )
    
    def test_subscription_creation(self):
        """Test creating a subscription."""
        subscription = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='active'
        )
        
        self.assertEqual(subscription.tenant, self.tenant)
        self.assertEqual(subscription.plan, self.plan)
        self.assertEqual(subscription.billing_cycle, 'monthly')
        self.assertEqual(subscription.status, 'active')
        self.assertIsNotNone(subscription.current_period_start)
        self.assertIsNotNone(subscription.current_period_end)
    
    def test_subscription_string_representation(self):
        """Test subscription string representation."""
        subscription = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='active'
        )
        
        expected = f"{self.tenant.name} - {self.plan.name} (monthly)"
        self.assertEqual(str(subscription), expected)
    
    def test_subscription_period_calculation_monthly(self):
        """Test subscription period calculation for monthly billing."""
        subscription = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='active'
        )
        
        # Check period is approximately 30 days
        period_length = subscription.current_period_end - subscription.current_period_start
        self.assertAlmostEqual(period_length.days, 30, delta=2)
    
    def test_subscription_period_calculation_yearly(self):
        """Test subscription period calculation for yearly billing."""
        subscription = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='yearly',
            status='active'
        )
        
        # Check period is approximately 365 days
        period_length = subscription.current_period_end - subscription.current_period_start
        self.assertAlmostEqual(period_length.days, 365, delta=2)
    
    def test_subscription_is_active_property(self):
        """Test subscription is_active property."""
        # Active subscription
        active_sub = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='active'
        )
        self.assertTrue(active_sub.is_active)
        
        # Cancelled subscription
        cancelled_sub = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='cancelled'
        )
        self.assertFalse(cancelled_sub.is_active)
        
        # Expired subscription
        expired_sub = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='expired'
        )
        self.assertFalse(expired_sub.is_active)
    
    def test_subscription_is_trial_property(self):
        """Test subscription is_trial property."""
        # Trial subscription
        trial_sub = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='trial'
        )
        self.assertTrue(trial_sub.is_trial)
        
        # Active subscription (not trial)
        active_sub = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='active'
        )
        self.assertFalse(active_sub.is_trial)
    
    def test_subscription_days_until_renewal(self):
        """Test days until renewal calculation."""
        subscription = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='active'
        )
        
        days_until = subscription.days_until_renewal()
        self.assertGreater(days_until, 0)
        self.assertLessEqual(days_until, 31)  # Should be within a month
    
    def test_subscription_calculate_current_price(self):
        """Test current price calculation based on billing cycle."""
        monthly_sub = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='active'
        )
        self.assertEqual(monthly_sub.calculate_current_price(), self.plan.price_monthly)
        
        yearly_sub = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='yearly',
            status='active'
        )
        self.assertEqual(yearly_sub.calculate_current_price(), self.plan.price_yearly)
    
    def test_subscription_unique_active_per_tenant(self):
        """Test that only one active subscription per tenant is allowed."""
        # Create first active subscription
        Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='active'
        )
        
        # Try to create second active subscription for same tenant
        with self.assertRaises(ValidationError):
            duplicate_sub = Subscription(
                tenant=self.tenant,
                plan=self.plan,
                billing_cycle='yearly',
                status='active'
            )
            duplicate_sub.full_clean()


class BillingHistoryModelTest(TransactionTestCase):
    """Test BillingHistory model functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create tenant and subscription
        self.tenant = Tenant.objects.create(
            name='Billing Test Corp',
            schema_name='billing_test'
        )
        
        self.plan = SubscriptionPlan.objects.create(
            name='Billing Test Plan',
            price_monthly=Decimal('29.99'),
            max_users=10,
            features={'basic_features': True}
        )
        
        self.subscription = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='active'
        )
    
    def test_billing_history_creation(self):
        """Test creating billing history entry."""
        billing = BillingHistory.objects.create(
            subscription=self.subscription,
            amount=Decimal('29.99'),
            billing_period_start=timezone.now().date(),
            billing_period_end=timezone.now().date() + timedelta(days=30),
            status='paid',
            transaction_id='txn_12345',
            payment_method='credit_card'
        )
        
        self.assertEqual(billing.subscription, self.subscription)
        self.assertEqual(billing.amount, Decimal('29.99'))
        self.assertEqual(billing.status, 'paid')
        self.assertEqual(billing.transaction_id, 'txn_12345')
    
    def test_billing_history_string_representation(self):
        """Test billing history string representation."""
        billing = BillingHistory.objects.create(
            subscription=self.subscription,
            amount=Decimal('29.99'),
            billing_period_start=timezone.now().date(),
            billing_period_end=timezone.now().date() + timedelta(days=30),
            status='paid'
        )
        
        expected = f"{self.tenant.name} - $29.99 - paid"
        self.assertEqual(str(billing), expected)
    
    def test_billing_history_amount_validation(self):
        """Test billing amount validation."""
        # Test negative amount
        with self.assertRaises(ValidationError):
            billing = BillingHistory(
                subscription=self.subscription,
                amount=Decimal('-10.00'),
                billing_period_start=timezone.now().date(),
                billing_period_end=timezone.now().date() + timedelta(days=30),
                status='pending'
            )
            billing.full_clean()
    
    def test_billing_history_period_validation(self):
        """Test billing period validation."""
        # Test end date before start date
        start_date = timezone.now().date()
        end_date = start_date - timedelta(days=1)  # Invalid: end before start
        
        with self.assertRaises(ValidationError):
            billing = BillingHistory(
                subscription=self.subscription,
                amount=Decimal('29.99'),
                billing_period_start=start_date,
                billing_period_end=end_date,
                status='pending'
            )
            billing.full_clean()
    
    def test_billing_history_ordering(self):
        """Test billing history ordering."""
        # Create multiple billing entries
        billing1 = BillingHistory.objects.create(
            subscription=self.subscription,
            amount=Decimal('29.99'),
            billing_period_start=timezone.now().date(),
            billing_period_end=timezone.now().date() + timedelta(days=30),
            status='paid',
            created_at=timezone.now() - timedelta(days=60)
        )
        
        billing2 = BillingHistory.objects.create(
            subscription=self.subscription,
            amount=Decimal('29.99'),
            billing_period_start=timezone.now().date(),
            billing_period_end=timezone.now().date() + timedelta(days=30),
            status='paid',
            created_at=timezone.now() - timedelta(days=30)
        )
        
        # Get ordered queryset (should be newest first)
        billings = BillingHistory.objects.all()
        self.assertEqual(billings[0], billing2)  # Most recent first
        self.assertEqual(billings[1], billing1)  # Older second


class SubscriptionPlanManagerTest(TestCase):
    """Test SubscriptionPlan custom manager functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create active plans
        self.active_plan1 = SubscriptionPlan.objects.create(
            name='Active Plan 1',
            price_monthly=Decimal('19.99'),
            max_users=5,
            is_active=True
        )
        
        self.active_plan2 = SubscriptionPlan.objects.create(
            name='Active Plan 2',
            price_monthly=Decimal('49.99'),
            max_users=25,
            is_active=True
        )
        
        # Create inactive plan
        self.inactive_plan = SubscriptionPlan.objects.create(
            name='Inactive Plan',
            price_monthly=Decimal('99.99'),
            max_users=100,
            is_active=False
        )
    
    def test_active_plans_manager(self):
        """Test active plans manager method."""
        active_plans = SubscriptionPlan.objects.active()
        
        self.assertEqual(active_plans.count(), 2)
        self.assertIn(self.active_plan1, active_plans)
        self.assertIn(self.active_plan2, active_plans)
        self.assertNotIn(self.inactive_plan, active_plans)
    
    def test_plans_by_price_range(self):
        """Test filtering plans by price range."""
        # Test if manager has method for price filtering
        cheap_plans = SubscriptionPlan.objects.filter(price_monthly__lt=Decimal('30.00'))
        expensive_plans = SubscriptionPlan.objects.filter(price_monthly__gte=Decimal('30.00'))
        
        self.assertIn(self.active_plan1, cheap_plans)
        self.assertIn(self.active_plan2, expensive_plans)
        self.assertIn(self.inactive_plan, expensive_plans)


class SubscriptionServiceTest(TransactionTestCase):
    """Test subscription-related service functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Service Test Corp',
            schema_name='service_test'
        )
        
        self.plan = SubscriptionPlan.objects.create(
            name='Service Test Plan',
            price_monthly=Decimal('39.99'),
            price_yearly=Decimal('399.99'),
            max_users=15,
            features={'test_feature': True}
        )
    
    def test_subscription_creation_service(self):
        """Test subscription creation through service layer."""
        # This would test a service method for creating subscriptions
        subscription_data = {
            'tenant': self.tenant,
            'plan': self.plan,
            'billing_cycle': 'monthly',
            'payment_method': 'credit_card'
        }
        
        # Create subscription
        subscription = Subscription.objects.create(
            tenant=subscription_data['tenant'],
            plan=subscription_data['plan'],
            billing_cycle=subscription_data['billing_cycle'],
            status='active'
        )
        
        self.assertEqual(subscription.tenant, self.tenant)
        self.assertEqual(subscription.plan, self.plan)
        self.assertTrue(subscription.is_active)
    
    def test_subscription_upgrade_service(self):
        """Test subscription plan upgrade."""
        # Create initial subscription
        original_subscription = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='active'
        )
        
        # Create premium plan
        premium_plan = SubscriptionPlan.objects.create(
            name='Premium Plan',
            price_monthly=Decimal('79.99'),
            max_users=50,
            features={'premium_feature': True}
        )
        
        # Simulate upgrade
        original_subscription.status = 'cancelled'
        original_subscription.save()
        
        upgraded_subscription = Subscription.objects.create(
            tenant=self.tenant,
            plan=premium_plan,
            billing_cycle='monthly',
            status='active'
        )
        
        self.assertFalse(original_subscription.is_active)
        self.assertTrue(upgraded_subscription.is_active)
        self.assertEqual(upgraded_subscription.plan, premium_plan)
    
    def test_subscription_cancellation_service(self):
        """Test subscription cancellation."""
        subscription = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='active'
        )
        
        # Simulate cancellation
        subscription.status = 'cancelled'
        subscription.cancelled_at = timezone.now()
        subscription.save()
        
        self.assertFalse(subscription.is_active)
        self.assertEqual(subscription.status, 'cancelled')
        self.assertIsNotNone(subscription.cancelled_at)
    
    @patch('apps.subscriptions.services.payment_processor.charge_customer')
    def test_billing_processing_service(self, mock_charge):
        """Test billing processing service."""
        mock_charge.return_value = {
            'success': True,
            'transaction_id': 'txn_test123',
            'amount': Decimal('39.99')
        }
        
        subscription = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='active'
        )
        
        # Simulate billing processing
        billing_result = mock_charge.return_value
        
        if billing_result['success']:
            BillingHistory.objects.create(
                subscription=subscription,
                amount=billing_result['amount'],
                billing_period_start=subscription.current_period_start,
                billing_period_end=subscription.current_period_end,
                status='paid',
                transaction_id=billing_result['transaction_id']
            )
        
        # Verify billing history was created
        billing_history = BillingHistory.objects.filter(subscription=subscription)
        self.assertEqual(billing_history.count(), 1)
        self.assertEqual(billing_history.first().status, 'paid')
        self.assertEqual(billing_history.first().transaction_id, 'txn_test123')


class SubscriptionAPITest(TestCase):
    """Test subscription-related API functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='API Test Corp',
            schema_name='api_test'
        )
        
        self.plan = SubscriptionPlan.objects.create(
            name='API Test Plan',
            price_monthly=Decimal('25.99'),
            max_users=10,
            is_active=True
        )
    
    def test_subscription_plan_list_api(self):
        """Test subscription plan list API endpoint."""
        # This would test the API endpoint for listing subscription plans
        active_plans = SubscriptionPlan.objects.filter(is_active=True)
        
        # Simulate API response
        api_response = [
            {
                'id': plan.id,
                'name': plan.name,
                'price_monthly': str(plan.price_monthly),
                'price_yearly': str(plan.price_yearly),
                'max_users': plan.max_users,
                'features': plan.features,
                'is_active': plan.is_active
            }
            for plan in active_plans
        ]
        
        self.assertEqual(len(api_response), 1)
        self.assertEqual(api_response[0]['name'], 'API Test Plan')
        self.assertTrue(api_response[0]['is_active'])
    
    def test_subscription_status_api(self):
        """Test subscription status API endpoint."""
        subscription = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='active'
        )
        
        # Simulate API response
        api_response = {
            'tenant_id': self.tenant.id,
            'plan_name': subscription.plan.name,
            'status': subscription.status,
            'billing_cycle': subscription.billing_cycle,
            'current_period_end': subscription.current_period_end.isoformat(),
            'days_until_renewal': subscription.days_until_renewal(),
            'is_active': subscription.is_active,
            'is_trial': subscription.is_trial
        }
        
        self.assertEqual(api_response['status'], 'active')
        self.assertEqual(api_response['plan_name'], 'API Test Plan')
        self.assertTrue(api_response['is_active'])
        self.assertFalse(api_response['is_trial'])


class SubscriptionIntegrationTest(TransactionTestCase):
    """Integration tests for subscription functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Integration Test Corp',
            schema_name='integration_test'
        )
        
        self.plan = SubscriptionPlan.objects.create(
            name='Integration Plan',
            price_monthly=Decimal('59.99'),
            max_users=30,
            features={'integration_test': True}
        )
    
    def test_complete_subscription_lifecycle(self):
        """Test complete subscription lifecycle."""
        # 1. Create subscription (trial)
        subscription = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='trial'
        )
        
        self.assertTrue(subscription.is_trial)
        self.assertFalse(subscription.is_active)
        
        # 2. Activate subscription
        subscription.status = 'active'
        subscription.save()
        
        self.assertFalse(subscription.is_trial)
        self.assertTrue(subscription.is_active)
        
        # 3. Create billing history
        billing = BillingHistory.objects.create(
            subscription=subscription,
            amount=subscription.calculate_current_price(),
            billing_period_start=subscription.current_period_start,
            billing_period_end=subscription.current_period_end,
            status='paid',
            transaction_id='test_txn_123'
        )
        
        self.assertEqual(billing.amount, self.plan.price_monthly)
        self.assertEqual(billing.status, 'paid')
        
        # 4. Cancel subscription
        subscription.status = 'cancelled'
        subscription.cancelled_at = timezone.now()
        subscription.save()
        
        self.assertFalse(subscription.is_active)
        self.assertEqual(subscription.status, 'cancelled')
        
        # Verify billing history is preserved
        billing_count = BillingHistory.objects.filter(subscription=subscription).count()
        self.assertEqual(billing_count, 1)
    
    def test_subscription_tenant_relationship(self):
        """Test subscription and tenant relationship integrity."""
        subscription = Subscription.objects.create(
            tenant=self.tenant,
            plan=self.plan,
            billing_cycle='monthly',
            status='active'
        )
        
        # Test relationship access
        self.assertEqual(subscription.tenant.name, 'Integration Test Corp')
        
        # Test reverse relationship
        tenant_subscriptions = self.tenant.subscriptions.all()
        self.assertIn(subscription, tenant_subscriptions)
        
        # Test subscription plan relationship
        self.assertEqual(subscription.plan.name, 'Integration Plan')
        
        # Test plan subscriptions
        plan_subscriptions = self.plan.subscriptions.all()
        self.assertIn(subscription, plan_subscriptions)
