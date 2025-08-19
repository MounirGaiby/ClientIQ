"""
Simple tests for platform app that work without multi-tenant setup.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from apps.platform.models import SuperUser
import uuid


class SuperUserModelTest(TestCase):
    """Simple test cases for SuperUser model."""

    def test_create_superuser(self):
        """Test creating a SuperUser."""
        unique_email = f"admin-{uuid.uuid4()}@platform.com"
        superuser = SuperUser.objects.create_user(
            email=unique_email,
            password='secure123',
            first_name='Admin',
            last_name='User'
        )
        
        self.assertEqual(superuser.email, unique_email)
        self.assertEqual(superuser.first_name, 'Admin')
        self.assertEqual(superuser.last_name, 'User')
        self.assertTrue(superuser.check_password('secure123'))

    def test_create_readonly_superuser(self):
        """Test creating a read-only SuperUser."""
        unique_email = f"readonly-{uuid.uuid4()}@platform.com"
        superuser = SuperUser.objects.create_user(
            email=unique_email,
            password='secure123',
            first_name='Read',
            last_name='Only',
            is_readonly=True
        )
        
        self.assertTrue(superuser.is_readonly)

    def test_superuser_str_representation(self):
        """Test string representation of SuperUser."""
        unique_email = f"admin-{uuid.uuid4()}@platform.com"
        superuser = SuperUser.objects.create_user(
            email=unique_email,
            password='secure123',
            first_name='Admin',
            last_name='User'
        )
        expected_str = f"{unique_email} (Platform Admin)"
        
        self.assertEqual(str(superuser), expected_str)

    def test_superuser_email_required(self):
        """Test email is required."""
        with self.assertRaises(TypeError):
            SuperUser.objects.create_user(
                password='password123',
                first_name='Test',
                last_name='User'
            )
