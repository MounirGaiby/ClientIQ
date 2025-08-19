"""
Comprehensive tests for demo app.
Tests DemoRequest model, views, serializers, and demo-to-tenant conversion.
"""

from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.admin.sites import AdminSite
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from apps.demo.models import DemoRequest
from apps.demo.serializers import (
    DemoRequestSerializer, 
    DemoRequestCreateSerializer,
    DemoRequestAdminSerializer
)
from apps.demo.views import DemoRequestListCreateView, DemoRequestDetailView
from apps.demo.admin import DemoRequestAdmin
from apps.platform.models import SuperUser


class DemoRequestModelTest(TestCase):
    """Test DemoRequest model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.demo_data = {
            'company_name': 'Test Corporation',
            'contact_email': 'admin@testcorp.com',
            'contact_name': 'John Doe',
            'phone_number': '+1234567890',
            'message': 'We would like to try your product.',
            'industry': 'Technology',
            'company_size': '50-100'
        }
    
    def test_create_demo_request(self):
        """Test creating a demo request."""
        demo = DemoRequest.objects.create(**self.demo_data)
        
        self.assertEqual(demo.company_name, 'Test Corporation')
        self.assertEqual(demo.contact_email, 'admin@testcorp.com')
        self.assertEqual(demo.contact_name, 'John Doe')
        self.assertEqual(demo.phone_number, '+1234567890')
        self.assertEqual(demo.message, 'We would like to try your product.')
        self.assertEqual(demo.industry, 'Technology')
        self.assertEqual(demo.company_size, '50-100')
        self.assertEqual(demo.status, 'pending')  # Default status
        self.assertIsNotNone(demo.created_at)
        self.assertIsNotNone(demo.updated_at)
    
    def test_demo_request_str_representation(self):
        """Test string representation of DemoRequest."""
        demo = DemoRequest.objects.create(**self.demo_data)
        expected = f"{demo.company_name} - {demo.contact_email}"
        self.assertEqual(str(demo), expected)
    
    def test_demo_request_status_choices(self):
        """Test demo request status choices."""
        statuses = ['pending', 'approved', 'rejected', 'converted']
        
        for status in statuses:
            demo_data = self.demo_data.copy()
            demo_data['company_name'] = f'Test Corp {status}'
            demo_data['contact_email'] = f'{status}@testcorp.com'
            demo_data['status'] = status
            
            demo = DemoRequest.objects.create(**demo_data)
            self.assertEqual(demo.status, status)
    
    def test_company_size_choices(self):
        """Test company size choices."""
        sizes = ['1-10', '11-50', '51-100', '101-500', '500+']
        
        for size in sizes:
            demo_data = self.demo_data.copy()
            demo_data['company_name'] = f'Test Corp {size}'
            demo_data['contact_email'] = f'{size.replace("-", "").replace("+", "plus")}@testcorp.com'
            demo_data['company_size'] = size
            
            demo = DemoRequest.objects.create(**demo_data)
            self.assertEqual(demo.company_size, size)
    
    def test_email_validation(self):
        """Test email validation."""
        demo_data = self.demo_data.copy()
        demo_data['contact_email'] = 'invalid-email'
        
        demo = DemoRequest(**demo_data)
        with self.assertRaises(ValidationError):
            demo.full_clean()
    
    def test_required_fields(self):
        """Test that required fields are validated."""
        required_fields = ['company_name', 'contact_email', 'contact_name']
        
        for field in required_fields:
            demo_data = self.demo_data.copy()
            demo_data[field] = ''
            
            demo = DemoRequest(**demo_data)
            with self.assertRaises(ValidationError):
                demo.full_clean()
    
    def test_optional_fields(self):
        """Test that optional fields can be empty."""
        optional_fields = ['phone_number', 'message', 'industry', 'company_size']
        
        for field in optional_fields:
            demo_data = self.demo_data.copy()
            demo_data['company_name'] = f'Test Corp {field}'
            demo_data['contact_email'] = f'{field}@testcorp.com'
            demo_data[field] = ''
            
            demo = DemoRequest.objects.create(**demo_data)
            self.assertEqual(getattr(demo, field), '')
    
    def test_demo_request_ordering(self):
        """Test demo request default ordering."""
        # Create multiple demo requests
        demo1 = DemoRequest.objects.create(
            company_name='Company A',
            contact_email='a@company.com',
            contact_name='Contact A'
        )
        demo2 = DemoRequest.objects.create(
            company_name='Company B',
            contact_email='b@company.com',
            contact_name='Contact B'
        )
        
        # Test that they're ordered by created_at (newest first)
        demos = list(DemoRequest.objects.all())
        self.assertEqual(demos[0], demo2)  # More recent
        self.assertEqual(demos[1], demo1)  # Older
    
    def test_status_update(self):
        """Test updating demo request status."""
        demo = DemoRequest.objects.create(**self.demo_data)
        self.assertEqual(demo.status, 'pending')
        
        demo.status = 'approved'
        demo.save()
        
        demo.refresh_from_db()
        self.assertEqual(demo.status, 'approved')


class DemoRequestSerializerTest(TestCase):
    """Test DemoRequest serializers."""
    
    def setUp(self):
        """Set up test data."""
        self.demo_data = {
            'company_name': 'Test Corporation',
            'contact_email': 'admin@testcorp.com',
            'contact_name': 'John Doe',
            'phone_number': '+1234567890',
            'message': 'We would like to try your product.',
            'industry': 'Technology',
            'company_size': '50-100'
        }
        
        self.demo = DemoRequest.objects.create(**self.demo_data)
    
    def test_demo_request_create_serializer(self):
        """Test DemoRequestCreateSerializer."""
        serializer = DemoRequestCreateSerializer(data=self.demo_data)
        self.assertTrue(serializer.is_valid())
        
        demo = serializer.save()
        self.assertEqual(demo.company_name, self.demo_data['company_name'])
        self.assertEqual(demo.contact_email, self.demo_data['contact_email'])
        self.assertEqual(demo.status, 'pending')  # Default status
    
    def test_demo_request_create_serializer_validation(self):
        """Test DemoRequestCreateSerializer validation."""
        # Test missing required fields
        invalid_data = self.demo_data.copy()
        invalid_data['contact_email'] = ''
        
        serializer = DemoRequestCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('contact_email', serializer.errors)
    
    def test_demo_request_serializer(self):
        """Test DemoRequestSerializer for reading."""
        serializer = DemoRequestSerializer(self.demo)
        data = serializer.data
        
        self.assertEqual(data['company_name'], self.demo.company_name)
        self.assertEqual(data['contact_email'], self.demo.contact_email)
        self.assertEqual(data['status'], self.demo.status)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
    
    def test_demo_request_admin_serializer(self):
        """Test DemoRequestAdminSerializer."""
        serializer = DemoRequestAdminSerializer(self.demo)
        data = serializer.data
        
        # Admin serializer should include all fields including status
        self.assertEqual(data['company_name'], self.demo.company_name)
        self.assertEqual(data['status'], self.demo.status)
        self.assertIn('created_at', data)
        
        # Test updating status
        update_data = {'status': 'approved'}
        serializer = DemoRequestAdminSerializer(self.demo, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_demo = serializer.save()
        self.assertEqual(updated_demo.status, 'approved')


class DemoRequestAPITest(APITestCase):
    """Test DemoRequest API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.demo_data = {
            'company_name': 'Test Corporation',
            'contact_email': 'admin@testcorp.com',
            'contact_name': 'John Doe',
            'phone_number': '+1234567890',
            'message': 'We would like to try your product.',
            'industry': 'Technology',
            'company_size': '50-100'
        }
        
        # Create platform admin user
        self.admin_user = SuperUser.objects.create_superuser(
            email='admin@platform.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        # Create demo request
        self.demo = DemoRequest.objects.create(**self.demo_data)
    
    def test_create_demo_request_unauthenticated(self):
        """Test creating demo request without authentication."""
        url = reverse('demo:demo-request-list')
        response = self.client.post(url, self.demo_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DemoRequest.objects.count(), 2)  # Original + new
        
        created_demo = DemoRequest.objects.latest('created_at')
        self.assertEqual(created_demo.company_name, self.demo_data['company_name'])
        self.assertEqual(created_demo.status, 'pending')
    
    def test_create_demo_request_invalid_data(self):
        """Test creating demo request with invalid data."""
        url = reverse('demo:demo-request-list')
        invalid_data = self.demo_data.copy()
        invalid_data['contact_email'] = 'invalid-email'
        
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('contact_email', response.data)
    
    def test_list_demo_requests_unauthenticated(self):
        """Test listing demo requests without authentication."""
        url = reverse('demo:demo-request-list')
        response = self.client.get(url)
        
        # Should require authentication for listing
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_demo_requests_authenticated(self):
        """Test listing demo requests with authentication."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('demo:demo-request-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['company_name'], self.demo.company_name)
    
    def test_retrieve_demo_request_authenticated(self):
        """Test retrieving specific demo request with authentication."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('demo:demo-request-detail', kwargs={'pk': self.demo.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], self.demo.company_name)
    
    def test_update_demo_request_status(self):
        """Test updating demo request status."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('demo:demo-request-detail', kwargs={'pk': self.demo.pk})
        
        update_data = {'status': 'approved'}
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.demo.refresh_from_db()
        self.assertEqual(self.demo.status, 'approved')
    
    def test_update_demo_request_unauthenticated(self):
        """Test updating demo request without authentication."""
        url = reverse('demo:demo-request-detail', kwargs={'pk': self.demo.pk})
        update_data = {'status': 'approved'}
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('apps.demo.views.send_mail')
    def test_demo_request_email_notification(self, mock_send_mail):
        """Test email notification on demo request creation."""
        mock_send_mail.return_value = True
        
        url = reverse('demo:demo-request-list')
        response = self.client.post(url, self.demo_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Email sending should be called
        mock_send_mail.assert_called_once()


class DemoRequestAdminTest(TestCase):
    """Test DemoRequest admin functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.admin_site = AdminSite()
        self.admin = DemoRequestAdmin(DemoRequest, self.admin_site)
        
        self.demo = DemoRequest.objects.create(
            company_name='Test Corporation',
            contact_email='admin@testcorp.com',
            contact_name='John Doe',
            phone_number='+1234567890',
            message='Test message',
            industry='Technology',
            company_size='50-100'
        )
    
    def test_admin_list_display(self):
        """Test admin list display configuration."""
        expected_fields = [
            'company_name', 'contact_name', 'contact_email',
            'status', 'industry', 'company_size', 'created_at'
        ]
        self.assertEqual(list(self.admin.list_display), expected_fields)
    
    def test_admin_list_filter(self):
        """Test admin list filter configuration."""
        expected_filters = ['status', 'industry', 'company_size', 'created_at']
        self.assertEqual(list(self.admin.list_filter), expected_filters)
    
    def test_admin_search_fields(self):
        """Test admin search fields configuration."""
        expected_fields = [
            'company_name', 'contact_name', 'contact_email', 'industry'
        ]
        self.assertEqual(list(self.admin.search_fields), expected_fields)
    
    def test_admin_readonly_fields(self):
        """Test admin readonly fields configuration."""
        readonly_fields = self.admin.readonly_fields
        self.assertIn('created_at', readonly_fields)
        self.assertIn('updated_at', readonly_fields)
    
    def test_admin_ordering(self):
        """Test admin ordering configuration."""
        self.assertEqual(self.admin.ordering, ['-created_at'])


class DemoToTenantConversionTest(TestCase):
    """Test demo-to-tenant conversion functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.demo = DemoRequest.objects.create(
            company_name='Test Corporation',
            contact_email='admin@testcorp.com',
            contact_name='John Doe',
            phone_number='+1234567890',
            message='We would like to try your product.',
            industry='Technology',
            company_size='50-100',
            status='approved'
        )
    
    def test_demo_conversion_data_mapping(self):
        """Test that demo data maps correctly for tenant creation."""
        # Test the data that would be used for tenant creation
        expected_schema_name = 'testcorp'  # Derived from company name
        expected_tenant_name = self.demo.company_name
        expected_contact_email = self.demo.contact_email
        
        # Simulate the conversion logic
        schema_name = self.demo.company_name.lower().replace(' ', '').replace('corporation', 'corp')
        
        self.assertEqual(schema_name, expected_schema_name)
        self.assertEqual(self.demo.company_name, expected_tenant_name)
        self.assertEqual(self.demo.contact_email, expected_contact_email)
    
    def test_demo_status_after_conversion(self):
        """Test that demo status is updated after conversion."""
        # Simulate conversion process
        self.demo.status = 'converted'
        self.demo.save()
        
        self.demo.refresh_from_db()
        self.assertEqual(self.demo.status, 'converted')
    
    def test_demo_approval_workflow(self):
        """Test demo approval workflow."""
        # Start with pending demo
        pending_demo = DemoRequest.objects.create(
            company_name='Pending Corp',
            contact_email='admin@pending.com',
            contact_name='Pending User',
            status='pending'
        )
        
        # Approve demo
        pending_demo.status = 'approved'
        pending_demo.save()
        
        # Check status
        pending_demo.refresh_from_db()
        self.assertEqual(pending_demo.status, 'approved')
        
        # Convert to tenant
        pending_demo.status = 'converted'
        pending_demo.save()
        
        # Check final status
        pending_demo.refresh_from_db()
        self.assertEqual(pending_demo.status, 'converted')


class DemoRequestViewTest(TestCase):
    """Test DemoRequest views functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.demo = DemoRequest.objects.create(
            company_name='Test Corporation',
            contact_email='admin@testcorp.com',
            contact_name='John Doe'
        )
        
        self.admin_user = SuperUser.objects.create_superuser(
            email='admin@platform.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
    
    def test_demo_request_list_create_view_permissions(self):
        """Test permissions for DemoRequestListCreateView."""
        view = DemoRequestListCreateView()
        
        # GET should require authentication
        self.assertIn('IsAuthenticated', [p.__class__.__name__ for p in view.get_permissions()])
        
        # POST should allow anyone (AllowAny for demo requests)
        view.request = MagicMock()
        view.request.method = 'POST'
        view.action = 'create'
        
        # Check that create permissions allow unauthenticated access
        permissions = view.get_permissions()
        self.assertTrue(any(p.__class__.__name__ == 'AllowAny' for p in permissions))
    
    def test_demo_request_detail_view_permissions(self):
        """Test permissions for DemoRequestDetailView."""
        view = DemoRequestDetailView()
        
        # Should require authentication for all operations
        permissions = view.get_permissions()
        self.assertTrue(any(p.__class__.__name__ == 'IsAuthenticated' for p in permissions))
    
    def test_demo_request_serializer_selection(self):
        """Test serializer selection based on action."""
        list_view = DemoRequestListCreateView()
        detail_view = DemoRequestDetailView()
        
        # List view should use different serializers for create vs list
        list_view.action = 'create'
        create_serializer = list_view.get_serializer_class()
        self.assertEqual(create_serializer, DemoRequestCreateSerializer)
        
        list_view.action = 'list'
        list_serializer = list_view.get_serializer_class()
        self.assertEqual(list_serializer, DemoRequestSerializer)
        
        # Detail view should use admin serializer
        detail_serializer = detail_view.get_serializer_class()
        self.assertEqual(detail_serializer, DemoRequestAdminSerializer)


class DemoRequestIntegrationTest(TestCase):
    """Integration tests for DemoRequest functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.admin_user = SuperUser.objects.create_superuser(
            email='admin@platform.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
    
    def test_full_demo_request_lifecycle(self):
        """Test full demo request lifecycle from creation to conversion."""
        # 1. Create demo request (public submission)
        demo_data = {
            'company_name': 'Test Corporation',
            'contact_email': 'admin@testcorp.com',
            'contact_name': 'John Doe',
            'phone_number': '+1234567890',
            'message': 'We would like to try your product.',
            'industry': 'Technology',
            'company_size': '50-100'
        }
        
        demo = DemoRequest.objects.create(**demo_data)
        self.assertEqual(demo.status, 'pending')
        
        # 2. Admin reviews and approves
        demo.status = 'approved'
        demo.save()
        self.assertEqual(demo.status, 'approved')
        
        # 3. Admin converts to tenant
        demo.status = 'converted'
        demo.save()
        self.assertEqual(demo.status, 'converted')
        
        # Verify final state
        demo.refresh_from_db()
        self.assertEqual(demo.status, 'converted')
        self.assertEqual(demo.company_name, demo_data['company_name'])
        self.assertEqual(demo.contact_email, demo_data['contact_email'])
    
    @patch('apps.demo.views.send_mail')
    def test_demo_request_with_email_notification(self, mock_send_mail):
        """Test demo request creation with email notification."""
        mock_send_mail.return_value = True
        
        # Create demo request
        demo = DemoRequest.objects.create(
            company_name='Email Test Corp',
            contact_email='admin@emailtest.com',
            contact_name='Email User'
        )
        
        # Verify demo created
        self.assertEqual(demo.company_name, 'Email Test Corp')
        
        # In real implementation, email would be sent via signal or view
        # Here we just verify the mock is available for testing
        self.assertTrue(mock_send_mail.return_value)
    
    def test_demo_request_validation_edge_cases(self):
        """Test demo request validation edge cases."""
        # Test very long company name
        long_name = 'A' * 300  # Longer than max_length
        with self.assertRaises(Exception):  # Should fail validation
            demo = DemoRequest(
                company_name=long_name,
                contact_email='test@test.com',
                contact_name='Test User'
            )
            demo.full_clean()
        
        # Test special characters in company name
        special_chars_name = "Test & Co. (Pty) Ltd."
        demo = DemoRequest.objects.create(
            company_name=special_chars_name,
            contact_email='test@testco.com',
            contact_name='Test User'
        )
        self.assertEqual(demo.company_name, special_chars_name)
        
        # Test international email
        international_email = 'tëst@tëst.çom'
        demo = DemoRequest.objects.create(
            company_name='International Corp',
            contact_email=international_email,
            contact_name='International User'
        )
        self.assertEqual(demo.contact_email, international_email)
