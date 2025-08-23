"""
Working tests for opportunities app.
"""
from django.test import TestCase
from django_tenants.test.cases import TenantTestCase
from django_tenants.utils import get_tenant_model, get_tenant_domain_model
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone

from apps.contacts.models import Contact, Company
from apps.opportunities.models import SalesStage, Opportunity, OpportunityHistory
from apps.users.models import CustomUser

class SalesStageModelTest(TenantTestCase):
    """Test SalesStage model functionality."""

    def setUp(self):
        super().setUp()
        # You can access self.tenant here if you need it
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_stage_creation(self):
        stage = SalesStage.objects.create(
            name="Test Stage",
            description="A test stage",
            order=1,
            probability=50.00,
        )
        self.assertEqual(stage.name, "Test Stage")
        self.assertEqual(stage.probability, 50.00)
        self.assertEqual(stage.order, 1)
        self.assertTrue(stage.is_active)
        self.assertFalse(stage.is_closed_won)
        self.assertFalse(stage.is_closed_lost)

    def test_closed_won_stage_probability(self):
        stage = SalesStage.objects.create(
            name="Closed Won",
            order=1,
            probability=75.00,  # should be overridden
            is_closed_won=True,
        )
        self.assertEqual(stage.probability, 100.00)
        self.assertTrue(stage.is_closed)

    def test_closed_lost_stage_probability(self):
        stage = SalesStage.objects.create(
            name="Closed Lost",
            order=1,
            probability=25.00,  # should be overridden
            is_closed_lost=True,
        )
        self.assertEqual(stage.probability, 0.00)
        self.assertTrue(stage.is_closed)


class OpportunityModelTest(TenantTestCase):
    """Test Opportunity model functionality within tenant schema."""

    def setUp(self):
        super().setUp()

        # Create user
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        # Create company
        self.company = Company.objects.create(
            name="Test Company",
            industry="Technology",
        )

        # Create contact
        self.contact = Contact.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@testcompany.com",
            company=self.company,
            contact_type="lead",
            owner=self.user,
        )

        # Create sales stage
        self.stage = SalesStage.objects.create(
            name="Qualified",
            order=1,
            probability=25.00,
        )

    def test_opportunity_creation(self):
        """Test creating an opportunity."""
        opportunity = Opportunity.objects.create(
            name="Test Deal",
            description="A test opportunity",
            value=Decimal("10000.00"),
            contact=self.contact,
            stage=self.stage,
            owner=self.user,
            priority="medium",
            expected_close_date=date.today() + timedelta(days=30),
        )

        self.assertEqual(opportunity.name, "Test Deal")
        self.assertEqual(opportunity.value, Decimal("10000.00"))
        self.assertEqual(opportunity.contact, self.contact)
        self.assertEqual(opportunity.company, self.company)  # Auto-set from contact
        self.assertEqual(opportunity.stage, self.stage)
        self.assertEqual(opportunity.probability, 25.00)  # From stage

    def test_weighted_value_calculation(self):
        """Test weighted value calculation."""
        opportunity = Opportunity.objects.create(
            name="Test Deal",
            value=Decimal("10000.00"),
            contact=self.contact,
            stage=self.stage,
            owner=self.user,
            probability=50.00,  # Override stage probability
        )

        expected_weighted_value = Decimal("5000.00")  # 10000 * 50% = 5000
        self.assertEqual(opportunity.weighted_value, expected_weighted_value)

    def test_is_overdue(self):
        """Test overdue detection."""
        # Create overdue opportunity
        past_date = date.today() - timedelta(days=5)
        overdue_opportunity = Opportunity.objects.create(
            name="Overdue Deal",
            value=Decimal("5000.00"),
            contact=self.contact,
            stage=self.stage,
            owner=self.user,
            expected_close_date=past_date,
        )
        self.assertTrue(overdue_opportunity.is_overdue)

        # Create future opportunity
        future_date = date.today() + timedelta(days=10)
        future_opportunity = Opportunity.objects.create(
            name="Future Deal",
            value=Decimal("7500.00"),
            contact=self.contact,
            stage=self.stage,
            owner=self.user,
            expected_close_date=future_date,
        )
        self.assertFalse(future_opportunity.is_overdue)

    def test_move_to_stage(self):
        """Test moving opportunity to new stage with history tracking."""
        opportunity = Opportunity.objects.create(
            name="Test Deal",
            value=Decimal("10000.00"),
            contact=self.contact,
            stage=self.stage,
            owner=self.user,
        )

        # Create new stage
        new_stage = SalesStage.objects.create(
            name="Proposal",
            order=2,
            probability=50.00,
        )

        # Move to new stage
        opportunity.move_to_stage(new_stage, self.user, "Moving to proposal stage")

        # Verify stage change
        opportunity.refresh_from_db()
        self.assertEqual(opportunity.stage, new_stage)
        self.assertEqual(opportunity.probability, 50.00)

        # Verify history was created
        history = OpportunityHistory.objects.filter(opportunity=opportunity).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.old_stage, self.stage)
        self.assertEqual(history.new_stage, new_stage)
        self.assertEqual(history.changed_by, self.user)

    def test_closed_stage_sets_actual_close_date(self):
        """Test that moving to closed stage sets actual close date."""
        opportunity = Opportunity.objects.create(
            name="Test Deal",
            value=Decimal("10000.00"),
            contact=self.contact,
            stage=self.stage,
            owner=self.user,
        )

        # Create closed won stage
        closed_stage = SalesStage.objects.create(
            name="Closed Won",
            order=3,
            probability=100.00,
            is_closed_won=True,
        )

        # Move to closed stage
        opportunity.move_to_stage(closed_stage, self.user)

        # Verify actual close date was set
        opportunity.refresh_from_db()
        self.assertIsNotNone(opportunity.actual_close_date)
        self.assertEqual(opportunity.actual_close_date, timezone.now().date())

class OpportunityHistoryTest(TenantTestCase):
    """Test OpportunityHistory model functionality."""
    
    def setUp(self):
        super().setUp()
        """Set up test data."""
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.company = Company.objects.create(
            name='Test Company',
            created_by=self.user
        )
        
        self.contact = Contact.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@testcompany.com',
            company=self.company,
            contact_type='lead',
            owner=self.user,
            created_by=self.user
        )
        
        self.stage = SalesStage.objects.create(
            name='Qualified',
            order=1,
            probability=25.00,
            created_by=self.user
        )
        
        self.opportunity = Opportunity.objects.create(
            name='Test Deal',
            value=Decimal('10000.00'),
            contact=self.contact,
            stage=self.stage,
            owner=self.user,
            created_by=self.user
        )
    
    def test_history_creation(self):
        """Test creating opportunity history."""
        history = OpportunityHistory.objects.create(
            opportunity=self.opportunity,
            action='created',
            new_stage=self.stage,
            new_value=self.opportunity.value,
            new_probability=self.opportunity.probability,
            changed_by=self.user,
            notes='Opportunity created'
        )
        
        self.assertEqual(history.opportunity, self.opportunity)
        self.assertEqual(history.action, 'created')
        self.assertEqual(history.new_stage, self.stage)
        self.assertEqual(history.changed_by, self.user)
    
    def test_stage_change_history(self):
        """Test history tracking for stage changes."""
        # Create new stage
        new_stage = SalesStage.objects.create(
            name='Proposal',
            order=2,
            probability=50.00,
            created_by=self.user
        )
        
        # Create history entry for stage change
        history = OpportunityHistory.objects.create(
            opportunity=self.opportunity,
            action='stage_changed',
            old_stage=self.stage,
            new_stage=new_stage,
            old_probability=25.00,
            new_probability=50.00,
            changed_by=self.user,
            notes=f'Stage changed from {self.stage} to {new_stage}'
        )
        
        self.assertEqual(history.old_stage, self.stage)
        self.assertEqual(history.new_stage, new_stage)
        self.assertEqual(history.old_probability, 25.00)
        self.assertEqual(history.new_probability, 50.00)


class OpportunityQueryTest(TenantTestCase):
    """Test opportunity querysets and filtering."""
    
    def setUp(self):
        super().setUp()
        """Set up test data."""
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.company = Company.objects.create(
            name='Test Company',
            created_by=self.user
        )
        
        self.contact = Contact.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@testcompany.com',
            company=self.company,
            contact_type='lead',
            owner=self.user,
            created_by=self.user
        )
        
        # Create multiple stages
        self.stage1 = SalesStage.objects.create(
            name='Lead',
            order=1,
            probability=10.00,
            created_by=self.user
        )
        
        self.stage2 = SalesStage.objects.create(
            name='Qualified',
            order=2,
            probability=25.00,
            created_by=self.user
        )
        
        self.closed_won = SalesStage.objects.create(
            name='Closed Won',
            order=3,
            probability=100.00,
            is_closed_won=True,
            created_by=self.user
        )
        
        # Create test opportunities
        Opportunity.objects.create(
            name='Deal 1',
            value=Decimal('5000.00'),
            contact=self.contact,
            stage=self.stage1,
            owner=self.user,
            priority='low',
            created_by=self.user
        )
        
        Opportunity.objects.create(
            name='Deal 2',
            value=Decimal('10000.00'),
            contact=self.contact,
            stage=self.stage2,
            owner=self.user,
            priority='high',
            created_by=self.user
        )
        
        Opportunity.objects.create(
            name='Deal 3',
            value=Decimal('15000.00'),
            contact=self.contact,
            stage=self.closed_won,
            owner=self.user,
            priority='medium',
            created_by=self.user
        )
    
    def test_filter_by_stage(self):
        """Test filtering opportunities by stage."""
        qualified_opps = Opportunity.objects.filter(stage=self.stage2)
        self.assertEqual(qualified_opps.count(), 1)
        self.assertEqual(qualified_opps.first().name, 'Deal 2')
    
    def test_filter_by_priority(self):
        """Test filtering opportunities by priority."""
        high_priority_opps = Opportunity.objects.filter(priority='high')
        self.assertEqual(high_priority_opps.count(), 1)
        self.assertEqual(high_priority_opps.first().name, 'Deal 2')
    
    def test_closed_opportunities(self):
        """Test filtering closed opportunities."""
        closed_opps = Opportunity.objects.filter(stage__is_closed_won=True)
        self.assertEqual(closed_opps.count(), 1)
        self.assertEqual(closed_opps.first().name, 'Deal 3')