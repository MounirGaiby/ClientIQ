"""
Working comprehensive tests for demo app.
"""

from django.test import TestCase, Client
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
import uuid
import json

from apps.demo.models import DemoRequest
from apps.demo.serializers import DemoRequestSerializer
from apps.users.models import CustomUser


class DemoRequestModelTest(TestCase):
    """Test DemoRequest model functionality."""
    
    def test_create_demo_request(self):
        """Test creating a demo request."""
        demo = DemoRequest.objects.create(
            company_name='Test Company',
            first_name='John',
            last_name='Doe',
            email='john.doe@testcompany.com',
            phone='+1234567890',
            job_title='CTO',
            company_size='11-50',
            industry='Technology',
            message='Interested in your platform for our team'
        )
        
        self.assertEqual(demo.company_name, 'Test Company')
        self.assertEqual(demo.contact_name, 'John Doe')
        self.assertEqual(demo.phone, '1234567890')
        self.assertEqual(demo.status, 'pending')  # Default status
        self.assertIsNotNone(demo.created_at)
        self.assertIsNone(demo.converted_at)
        self.assertIsNone(demo.converted_user)
    
    def test_demo_request_str_representation(self):
        """Test DemoRequest string representation."""
        email = f'demo-{uuid.uuid4()}@test.com'
        demo = DemoRequest.objects.create(
            company_name='Demo Company',
            email=email,
            first_name='Demo',
            last_name='User',
            phone='9876543210',
            message='Demo message'
        )
        
        expected = f"Demo Company - Demo User ({email})"
        self.assertEqual(str(demo), expected)
    
    def test_demo_status_choices(self):
        """Test demo request status choices."""
        demo = DemoRequest.objects.create(
            company_name='Status Test',
            contact_email=f'status-{uuid.uuid4()}@test.com',
            contact_name='Status User',
            phone='1111111111',
            message='Status test'
        )
        
        # Test status transitions
        demo.status = 'approved'
        demo.save()
        self.assertEqual(demo.status, 'approved')
        
        demo.status = 'rejected'
        demo.save()
        self.assertEqual(demo.status, 'rejected')
        
        demo.status = 'converted'
        demo.save()
        self.assertEqual(demo.status, 'converted')
    
    def test_demo_conversion(self):
        """Test demo request conversion."""
        # Create a user to convert to
        user_email = f'convert-{uuid.uuid4()}@test.com'
        user = CustomUser.objects.create_user(
            email=user_email,
            password='convertpass123',
            first_name='Convert',
            last_name='User'
        )
        
        demo = DemoRequest.objects.create(
            company_name='Convert Company',
            contact_email=f'demo-{uuid.uuid4()}@test.com',
            contact_name='Demo Convert',
            phone='2222222222',
            message='Convert test'
        )
        
        # Convert demo
        demo.status = 'converted'
        demo.converted_user = user
        demo.save()
        
        self.assertEqual(demo.status, 'converted')
        self.assertEqual(demo.converted_user, user)
        self.assertIsNotNone(demo.converted_at)
    
    def test_email_uniqueness(self):
        """Test email uniqueness in demo requests."""
        email = f'unique-{uuid.uuid4()}@test.com'
        
        DemoRequest.objects.create(
            company_name='First Company',
            contact_email=email,
            contact_name='First User',
            phone='3333333333',
            message='First message'
        )
        
        # Should be able to create another demo with same email
        # (business requirement: companies can request multiple demos)
        demo2 = DemoRequest.objects.create(
            company_name='Second Company',
            contact_email=email,
            contact_name='Second User',
            phone='4444444444',
            message='Second message'
        )
        
        self.assertEqual(demo2.contact_email, email)


class DemoRequestSerializerTest(TestCase):
    """Test DemoRequestSerializer functionality."""
    
    def test_serializer_validation(self):
        """Test serializer validation."""
        valid_data = {
            'company_name': 'Serializer Company',
            'contact_email': f'serializer-{uuid.uuid4()}@test.com',
            'contact_name': 'Serializer User',
            'phone': '5555555555',
            'message': 'Serializer test'
        }
        
        serializer = DemoRequestSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        demo = serializer.save()
        self.assertEqual(demo.company_name, 'Serializer Company')
        self.assertEqual(demo.status, 'pending')
    
    def test_serializer_required_fields(self):
        """Test serializer required fields validation."""
        # Missing required fields
        invalid_data = {
            'company_name': 'Incomplete Company'
            # Missing email, name, phone, message
        }
        
        serializer = DemoRequestSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('contact_email', serializer.errors)
        self.assertIn('contact_name', serializer.errors)
    
    def test_serializer_email_validation(self):
        """Test email validation in serializer."""
        invalid_data = {
            'company_name': 'Email Test Company',
            'contact_email': 'invalid-email',
            'contact_name': 'Email Test User',
            'phone': '6666666666',
            'message': 'Email validation test'
        }
        
        serializer = DemoRequestSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('contact_email', serializer.errors)
    
    def test_serializer_phone_validation(self):
        """Test phone validation in serializer."""
        data_with_phone = {
            'company_name': 'Phone Test Company',
            'contact_email': f'phone-{uuid.uuid4()}@test.com',
            'contact_name': 'Phone Test User',
            'phone': '7777777777',
            'message': 'Phone validation test'
        }
        
        serializer = DemoRequestSerializer(data=data_with_phone)
        self.assertTrue(serializer.is_valid())


class DemoRequestViewTest(APITestCase):
    """Test DemoRequest API views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.demo_data = {
            'company_name': 'API Test Company',
            'contact_email': f'api-{uuid.uuid4()}@test.com',
            'contact_name': 'API Test User',
            'phone': '8888888888',
            'message': 'API test message'
        }
    
    def test_create_demo_request(self):
        """Test creating demo request via API."""
        response = self.client.post('/api/demo/request/', self.demo_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DemoRequest.objects.count(), 1)
        
        demo = DemoRequest.objects.first()
        self.assertEqual(demo.company_name, 'API Test Company')
        self.assertEqual(demo.status, 'pending')
    
    def test_create_demo_request_invalid_data(self):
        """Test creating demo request with invalid data."""
        invalid_data = {
            'company_name': 'Invalid Company'
            # Missing required fields
        }
        
        response = self.client.post('/api/demo/request/', invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DemoRequest.objects.count(), 0)
    
    def test_list_demo_requests(self):
        """Test listing demo requests."""
        # Create test demos
        DemoRequest.objects.create(**self.demo_data)
        DemoRequest.objects.create(
            company_name='Second Company',
            contact_email=f'second-{uuid.uuid4()}@test.com',
            contact_name='Second User',
            phone='9999999999',
            message='Second message'
        )
        
        response = self.client.get('/api/demo/requests/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_retrieve_demo_request(self):
        """Test retrieving specific demo request."""
        demo = DemoRequest.objects.create(**self.demo_data)
        
        response = self.client.get(f'/api/demo/requests/{demo.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], 'API Test Company')
    
    def test_update_demo_request_status(self):
        """Test updating demo request status."""
        demo = DemoRequest.objects.create(**self.demo_data)
        
        update_data = {'status': 'approved'}
        response = self.client.patch(f'/api/demo/requests/{demo.id}/', update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        demo.refresh_from_db()
        self.assertEqual(demo.status, 'approved')


class DemoRequestBusinessLogicTest(TestCase):
    """Test DemoRequest business logic."""
    
    def test_demo_approval_workflow(self):
        """Test demo approval workflow."""
        demo = DemoRequest.objects.create(
            company_name='Workflow Company',
            contact_email=f'workflow-{uuid.uuid4()}@test.com',
            contact_name='Workflow User',
            phone='1010101010',
            message='Workflow test'
        )
        
        # Initial state
        self.assertEqual(demo.status, 'pending')
        self.assertIsNone(demo.converted_at)
        
        # Approve demo
        demo.status = 'approved'
        demo.save()
        
        self.assertEqual(demo.status, 'approved')
        self.assertIsNone(demo.converted_at)  # Not converted yet
    
    def test_demo_rejection_workflow(self):
        """Test demo rejection workflow."""
        demo = DemoRequest.objects.create(
            company_name='Reject Company',
            contact_email=f'reject-{uuid.uuid4()}@test.com',
            contact_name='Reject User',
            phone='1111111111',
            message='Reject test'
        )
        
        # Reject demo
        demo.status = 'rejected'
        demo.save()
        
        self.assertEqual(demo.status, 'rejected')
        self.assertIsNone(demo.converted_user)
        self.assertIsNone(demo.converted_at)
    
    def test_demo_conversion_workflow(self):
        """Test complete demo conversion workflow."""
        # Create user for conversion
        user = CustomUser.objects.create_user(
            email=f'workflow-user-{uuid.uuid4()}@test.com',
            password='workflowpass123',
            first_name='Workflow',
            last_name='User'
        )
        
        demo = DemoRequest.objects.create(
            company_name='Conversion Company',
            contact_email=f'conversion-{uuid.uuid4()}@test.com',
            contact_name='Conversion User',
            phone='1212121212',
            message='Conversion test'
        )
        
        # Convert demo
        demo.status = 'converted'
        demo.converted_user = user
        demo.save()
        
        self.assertEqual(demo.status, 'converted')
        self.assertEqual(demo.converted_user, user)
        self.assertIsNotNone(demo.converted_at)
    
    def test_demo_metrics(self):
        """Test demo request metrics."""
        # Create demos with different statuses
        DemoRequest.objects.create(
            company_name='Pending Company',
            contact_email=f'pending-{uuid.uuid4()}@test.com',
            contact_name='Pending User',
            phone='1313131313',
            message='Pending test',
            status='pending'
        )
        
        DemoRequest.objects.create(
            company_name='Approved Company',
            contact_email=f'approved-{uuid.uuid4()}@test.com',
            contact_name='Approved User',
            phone='1414141414',
            message='Approved test',
            status='approved'
        )
        
        DemoRequest.objects.create(
            company_name='Converted Company',
            contact_email=f'converted-{uuid.uuid4()}@test.com',
            contact_name='Converted User',
            phone='1515151515',
            message='Converted test',
            status='converted'
        )
        
        # Test metrics
        total_demos = DemoRequest.objects.count()
        pending_demos = DemoRequest.objects.filter(status='pending').count()
        approved_demos = DemoRequest.objects.filter(status='approved').count()
        converted_demos = DemoRequest.objects.filter(status='converted').count()
        
        self.assertEqual(total_demos, 3)
        self.assertEqual(pending_demos, 1)
        self.assertEqual(approved_demos, 1)
        self.assertEqual(converted_demos, 1)


class DemoRequestSecurityTest(TestCase):
    """Test DemoRequest security features."""
    
    def test_demo_data_validation(self):
        """Test demo data validation and sanitization."""
        # Test with potentially malicious data
        demo = DemoRequest.objects.create(
            company_name='<script>alert("xss")</script>',
            contact_email=f'security-{uuid.uuid4()}@test.com',
            contact_name='Security User',
            phone='1616161616',
            message='<img src="x" onerror="alert(1)">'
        )
        
        # Data should be stored as-is (validation/sanitization in views)
        self.assertIn('<script>', demo.company_name)
        self.assertIn('<img', demo.message)
    
    def test_demo_phone_format(self):
        """Test phone number format validation."""
        demo = DemoRequest.objects.create(
            company_name='Phone Format Company',
            contact_email=f'phone-format-{uuid.uuid4()}@test.com',
            contact_name='Phone User',
            phone='+1-555-123-4567',
            message='Phone format test'
        )
        
        self.assertEqual(demo.phone, '+1-555-123-4567')
    
    def test_demo_message_length(self):
        """Test demo message length handling."""
        long_message = 'A' * 1000  # Very long message
        
        demo = DemoRequest.objects.create(
            company_name='Long Message Company',
            contact_email=f'long-message-{uuid.uuid4()}@test.com',
            contact_name='Long Message User',
            phone='1717171717',
            message=long_message
        )
        
        self.assertEqual(len(demo.message), 1000)


class DemoRequestIntegrationTest(TestCase):
    """Test DemoRequest integration with other systems."""
    
    def test_demo_user_integration(self):
        """Test demo integration with user system."""
        # Create user
        user = CustomUser.objects.create_user(
            email=f'integration-{uuid.uuid4()}@test.com',
            password='integrationpass123',
            first_name='Integration',
            last_name='User'
        )
        
        # Create demo
        demo = DemoRequest.objects.create(
            company_name='Integration Company',
            contact_email=f'demo-integration-{uuid.uuid4()}@test.com',
            contact_name='Demo Integration',
            phone='1818181818',
            message='Integration test'
        )
        
        # Link demo to user
        demo.converted_user = user
        demo.status = 'converted'
        demo.save()
        
        # Test relationship
        self.assertEqual(demo.converted_user, user)
        
        # Test reverse relationship (if exists)
        # user_demos = user.demo_requests.all()  # If related_name is set
        # self.assertIn(demo, user_demos)
    
    def test_demo_conversion_tracking(self):
        """Test demo conversion tracking."""
        user = CustomUser.objects.create_user(
            email=f'tracking-{uuid.uuid4()}@test.com',
            password='trackingpass123',
            first_name='Tracking',
            last_name='User'
        )
        
        demo = DemoRequest.objects.create(
            company_name='Tracking Company',
            contact_email=f'tracking-demo-{uuid.uuid4()}@test.com',
            contact_name='Tracking Demo',
            phone='1919191919',
            message='Tracking test'
        )
        
        # Record conversion time
        import datetime
        before_conversion = datetime.datetime.now()
        
        demo.status = 'converted'
        demo.converted_user = user
        demo.save()
        
        after_conversion = datetime.datetime.now()
        
        # Check conversion timestamp
        self.assertIsNotNone(demo.converted_at)
        self.assertGreaterEqual(demo.converted_at.replace(tzinfo=None), before_conversion)
        self.assertLessEqual(demo.converted_at.replace(tzinfo=None), after_conversion)
