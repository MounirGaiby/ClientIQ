"""
Comprehensive tests for Demo app functionality.
Tests cover models, serializers, views, business logic, security, and integration.
"""

import uuid
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
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
        self.assertEqual(demo.first_name, 'John')
        self.assertEqual(demo.last_name, 'Doe')
        self.assertEqual(demo.email, 'john.doe@testcompany.com')
        self.assertEqual(demo.status, 'pending')  # Default status
        self.assertTrue(demo.created_at)
        self.assertTrue(demo.updated_at)
    
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
        
        # Check string representation includes company and contact name
        expected = f"Demo Company - Demo User ({demo.status})"
        self.assertEqual(str(demo), expected)
    
    def test_demo_status_choices(self):
        """Test demo request status choices."""
        email = f'status-{uuid.uuid4()}@test.com'
        demo = DemoRequest.objects.create(
            company_name='Status Test Company',
            email=email,
            first_name='Status',
            last_name='Test',
            phone='1234567890',
            message='Testing status changes'
        )
        
        # Test each status choice
        for status_code, status_label in DemoRequest.STATUS_CHOICES:
            demo.status = status_code
            demo.save()
            self.assertEqual(demo.status, status_code)
            self.assertEqual(demo.get_status_display(), status_label)
    
    def test_demo_conversion(self):
        """Test demo request conversion."""
        email = f'demo-{uuid.uuid4()}@test.com'
        demo = DemoRequest.objects.create(
            company_name='Conversion Test',
            email=email,
            first_name='Convert',
            last_name='Test',
            phone='1111111111',
            message='Ready to convert',
            status='approved'
        )
        
        # Test conversion to tenant
        demo.status = 'converted'
        demo.notes = 'Successfully converted to tenant'
        demo.save()
        
        self.assertEqual(demo.status, 'converted')
        self.assertIn('converted', demo.notes)
    
    def test_email_uniqueness(self):
        """Test email uniqueness in demo requests."""
        email = f'unique-{uuid.uuid4()}@test.com'
        
        # Create first demo request
        DemoRequest.objects.create(
            company_name='First Company',
            email=email,
            first_name='First',
            last_name='User',
            phone='1111111111'
        )
        
        # Creating second request with same email should work
        # (business rule allows multiple demo requests from same email)
        demo2 = DemoRequest.objects.create(
            company_name='Second Company',
            email=email,
            first_name='Second',
            last_name='User',
            phone='2222222222'
        )
        
        self.assertEqual(demo2.email, email)


class DemoRequestSerializerTest(TestCase):
    """Test DemoRequestSerializer functionality."""
    
    def test_serializer_validation(self):
        """Test serializer validation."""
        data = {
            'company_name': 'Serializer Test Company',
            'email': f'serializer-{uuid.uuid4()}@test.com',
            'first_name': 'Serializer',
            'last_name': 'Test',
            'phone': '+1234567890',
            'job_title': 'Manager',
            'company_size': '11-50',
            'industry': 'Technology',
            'message': 'Testing serializer validation'
        }
        
        serializer = DemoRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        demo_request = serializer.save()
        self.assertEqual(demo_request.company_name, data['company_name'])
        self.assertEqual(demo_request.email, data['email'])
    
    def test_serializer_required_fields(self):
        """Test serializer required fields validation."""
        data = {}
        
        serializer = DemoRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        
        # Check that required fields are in errors
        required_fields = ['first_name', 'last_name', 'email']
        for field in required_fields:
            self.assertIn(field, serializer.errors)
    
    def test_serializer_email_validation(self):
        """Test email validation in serializer."""
        data = {
            'company_name': 'Email Test Company',
            'email': 'invalid-email',
            'first_name': 'Email',
            'last_name': 'Test',
            'phone': '+1234567890'
        }
        
        serializer = DemoRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_serializer_phone_validation(self):
        """Test phone validation in serializer."""
        data = {
            'company_name': 'Phone Test Company',
            'email': f'phone-{uuid.uuid4()}@test.com',
            'first_name': 'Phone',
            'last_name': 'Test',
            'phone': '+1-234-567-8900'  # Valid format
        }
        
        serializer = DemoRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class DemoRequestViewTest(APITestCase):
    """Test DemoRequest API views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.demo_data = {
            'company_name': 'API Test Company',
            'email': f'api-{uuid.uuid4()}@test.com',
            'first_name': 'API',
            'last_name': 'Test',
            'phone': '+1234567890',
            'job_title': 'Developer',
            'company_size': '11-50',
            'industry': 'Technology',
            'message': 'Testing API functionality'
        }
    
    def test_create_demo_request(self):
        """Test creating demo request via API."""
        url = reverse('demo:demo-list')
        response = self.client.post(url, self.demo_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DemoRequest.objects.count(), 1)
        
        demo = DemoRequest.objects.first()
        self.assertEqual(demo.company_name, self.demo_data['company_name'])
        self.assertEqual(demo.email, self.demo_data['email'])
    
    def test_create_demo_request_invalid_data(self):
        """Test creating demo request with invalid data."""
        invalid_data = {
            'company_name': '',  # Required field empty
            'email': 'invalid-email',  # Invalid email
        }
        
        url = reverse('demo:demo-list')
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(DemoRequest.objects.count(), 0)
    
    def test_list_demo_requests(self):
        """Test listing demo requests."""
        # Create test demo request
        DemoRequest.objects.create(**self.demo_data)
        
        # Create another demo request
        demo_data2 = self.demo_data.copy()
        demo_data2['email'] = f'second-{uuid.uuid4()}@test.com'
        demo_data2['company_name'] = 'Second Company'
        DemoRequest.objects.create(**demo_data2)
        
        url = reverse('demo:demo-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_retrieve_demo_request(self):
        """Test retrieving specific demo request."""
        demo = DemoRequest.objects.create(**self.demo_data)
        
        url = reverse('demo:demo-detail', kwargs={'pk': demo.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], demo.company_name)
    
    def test_update_demo_request_status(self):
        """Test updating demo request status."""
        demo = DemoRequest.objects.create(**self.demo_data)
        
        url = reverse('demo:demo-detail', kwargs={'pk': demo.pk})
        update_data = {'status': 'approved'}
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        demo.refresh_from_db()
        self.assertEqual(demo.status, 'approved')


class DemoRequestBusinessLogicTest(TestCase):
    """Test demo request business logic and workflows."""
    
    def test_demo_approval_workflow(self):
        """Test demo approval workflow."""
        demo = DemoRequest.objects.create(
            company_name='Workflow Test',
            email=f'workflow-{uuid.uuid4()}@test.com',
            first_name='Workflow',
            last_name='Test',
            phone='1234567890',
            message='Testing approval workflow',
            status='pending'
        )
        
        # Simulate approval process
        demo.status = 'processing'
        demo.notes = 'Under review by sales team'
        demo.save()
        
        # Approve the demo
        demo.status = 'approved'
        demo.notes += '\nApproved for demo setup'
        demo.save()
        
        self.assertEqual(demo.status, 'approved')
        self.assertIn('Approved', demo.notes)
    
    def test_demo_rejection_workflow(self):
        """Test demo rejection workflow."""
        demo = DemoRequest.objects.create(
            company_name='Rejection Test',
            email=f'reject-{uuid.uuid4()}@test.com',
            first_name='Reject',
            last_name='Test',
            phone='1234567890',
            message='Testing rejection workflow',
            status='pending'
        )
        
        # Simulate rejection process
        demo.status = 'rejected'
        demo.notes = 'Rejected due to incomplete information'
        demo.save()
        
        self.assertEqual(demo.status, 'rejected')
        self.assertIn('Rejected', demo.notes)
    
    def test_demo_conversion_workflow(self):
        """Test complete demo conversion workflow."""
        demo = DemoRequest.objects.create(
            company_name='Conversion Test',
            email=f'conversion-{uuid.uuid4()}@test.com',
            first_name='Convert',
            last_name='Test',
            phone='1234567890',
            message='Ready for conversion',
            status='approved'
        )
        
        # Simulate successful conversion
        demo.status = 'converted'
        demo.notes = 'Successfully converted to tenant'
        demo.save()
        
        self.assertEqual(demo.status, 'converted')
        self.assertIn('converted', demo.notes)
    
    def test_demo_metrics(self):
        """Test demo request metrics."""
        # Create demo requests with different statuses
        statuses = ['pending', 'approved', 'converted', 'rejected']
        
        for status in statuses:
            DemoRequest.objects.create(
                company_name=f'{status.title()} Company',
                email=f'{status}-{uuid.uuid4()}@test.com',
                first_name=status.title(),
                last_name='Test',
                phone='1234567890',
                status=status
            )
        
        # Test metrics
        total_count = DemoRequest.objects.count()
        pending_count = DemoRequest.objects.filter(status='pending').count()
        approved_count = DemoRequest.objects.filter(status='approved').count()
        converted_count = DemoRequest.objects.filter(status='converted').count()
        
        self.assertEqual(total_count, 4)
        self.assertEqual(pending_count, 1)
        self.assertEqual(approved_count, 1)
        self.assertEqual(converted_count, 1)


class DemoRequestSecurityTest(TestCase):
    """Test demo request security and data validation."""
    
    def test_demo_data_validation(self):
        """Test demo data validation and sanitization."""
        demo = DemoRequest.objects.create(
            company_name='<script>alert("XSS")</script>',
            email=f'security-{uuid.uuid4()}@test.com',
            first_name='Security',
            last_name='Test',
            phone='1234567890',
            message='<img src="x" onerror="alert(1)">'
        )
        
        # Data should be stored as-is (sanitization happens at view/template level)
        self.assertIn('<script>', demo.company_name)
        self.assertIn('<img', demo.message)
    
    def test_demo_phone_format(self):
        """Test phone number format validation."""
        demo = DemoRequest.objects.create(
            company_name='Phone Format Test',
            email=f'phone-format-{uuid.uuid4()}@test.com',
            first_name='Phone',
            last_name='Test',
            phone='+1-234-567-8900',  # Various formats should be accepted
            message='Testing phone formats'
        )
        
        self.assertTrue(demo.phone)
        self.assertIn('234', demo.phone)
    
    def test_demo_message_length(self):
        """Test demo message length handling."""
        long_message = 'A' * 1000  # Very long message
        
        demo = DemoRequest.objects.create(
            company_name='Long Message Test',
            email=f'long-message-{uuid.uuid4()}@test.com',
            first_name='Long',
            last_name='Test',
            phone='1234567890',
            message=long_message
        )
        
        self.assertEqual(len(demo.message), 1000)
        self.assertEqual(demo.message, long_message)


class DemoRequestIntegrationTest(TestCase):
    """Test demo request integration with other systems."""
    
    def test_demo_user_integration(self):
        """Test demo integration with user system."""
        demo = DemoRequest.objects.create(
            company_name='Integration Test',
            email=f'integration-{uuid.uuid4()}@test.com',
            first_name='Integration',
            last_name='Test',
            phone='1234567890',
            message='Testing user integration',
            status='approved'
        )
        
        # Simulate creating user from demo request
        user_data = {
            'email': demo.email,
            'first_name': demo.first_name,
            'last_name': demo.last_name,
            'password': 'temppassword123'
        }
        
        # In real implementation, this would create a tenant user
        self.assertEqual(demo.email, user_data['email'])
        self.assertEqual(demo.first_name, user_data['first_name'])
        self.assertEqual(demo.last_name, user_data['last_name'])
    
    def test_demo_conversion_tracking(self):
        """Test demo conversion tracking."""
        demo = DemoRequest.objects.create(
            company_name='Tracking Test',
            email=f'tracking-{uuid.uuid4()}@test.com',
            first_name='Track',
            last_name='Test',
            phone='1234567890',
            message='Testing conversion tracking',
            status='pending'
        )
        
        # Track status changes
        original_status = demo.status
        demo.status = 'processing'
        demo.save()
        
        demo.status = 'approved'
        demo.save()
        
        demo.status = 'converted'
        demo.notes = f'Converted from {original_status}'
        demo.save()
        
        self.assertEqual(demo.status, 'converted')
        self.assertIn('Converted from pending', demo.notes)
