from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .factories import UserFactory, AdminUserFactory, SuperAdminUserFactory, SellerUserFactory

User = get_user_model()

class UserModelTest(TestCase):
    """Test User model"""
    
    def test_create_user(self):
        user = UserFactory()
        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.role, 'user')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
    
    def test_create_admin_user(self):
        admin = AdminUserFactory()
        self.assertEqual(admin.role, 'admin')
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_admin)
    
    def test_create_super_admin_user(self):
        super_admin = SuperAdminUserFactory()
        self.assertEqual(super_admin.role, 'super_admin')
        self.assertTrue(super_admin.is_staff)
        self.assertTrue(super_admin.is_superuser)
        self.assertTrue(super_admin.is_super_admin)
    
    def test_phone_number_unique(self):
        user1 = UserFactory(phone_number='+998901234567')
        with self.assertRaises(Exception):
            UserFactory(phone_number='+998901234567')

class AuthenticationAPITest(APITestCase):
    """Test authentication endpoints"""
    
    def setUp(self):
        self.user = UserFactory(phone_number='+998901234567')
        self.user.set_password('testpass123')
        self.user.save()
    
    def test_user_login_success(self):
        """Test successful login"""
        url = reverse('accounts:login')
        data = {
            'phone_number': '+998901234567',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('user', response.data)
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = reverse('accounts:login')
        data = {
            'phone_number': '+998901234567',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_login_missing_fields(self):
        """Test login with missing fields"""
        url = reverse('accounts:login')
        data = {'phone_number': '+998901234567'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_registration_success(self):
        """Test successful registration"""
        url = reverse('accounts:register')
        data = {
            'full_name': 'Test User',
            'phone_number': '+998901234568',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access_token', response.data)
        self.assertIn('user', response.data)
        
        # Check user was created
        user = User.objects.get(phone_number='+998901234568')
        self.assertEqual(user.full_name, 'Test User')
    
    def test_user_registration_password_mismatch(self):
        """Test registration with password mismatch"""
        url = reverse('accounts:register')
        data = {
            'full_name': 'Test User',
            'phone_number': '+998901234569',
            'password': 'testpass123',
            'password_confirm': 'differentpass'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_duplicate_phone(self):
        """Test registration with duplicate phone number"""
        url = reverse('accounts:register')
        data = {
            'full_name': 'Test User',
            'phone_number': '+998901234567',  # Already exists
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserProfileAPITest(APITestCase):
    """Test user profile endpoints"""
    
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
    
    def test_get_user_profile(self):
        """Test getting current user profile"""
        url = reverse('accounts:profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['phone_number'], self.user.phone_number)
    
    def test_update_user_profile(self):
        """Test updating user profile"""
        url = reverse('accounts:profile_edit')
        data = {
            'full_name': 'Updated Name',
            'phone_number': self.user.phone_number
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, 'Updated Name')
    
    def test_profile_requires_authentication(self):
        """Test that profile endpoints require authentication"""
        self.client.force_authenticate(user=None)
        url = reverse('accounts:profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AdminUserManagementTest(APITestCase):
    """Test admin user management endpoints"""
    
    def setUp(self):
        self.admin = AdminUserFactory()
        self.super_admin = SuperAdminUserFactory()
        self.regular_user = UserFactory()
        
    def test_admin_can_list_users(self):
        """Test admin can list users"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('accounts:admin_users')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_admin_can_create_user(self):
        """Test admin can create users"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('accounts:admin_users')
        data = {
            'full_name': 'New User',
            'phone_number': '+998901234570',
            'password': 'testpass123',
            'role': 'user'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(phone_number='+998901234570').exists())
    
    def test_regular_user_cannot_access_admin_endpoints(self):
        """Test regular users cannot access admin endpoints"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('accounts:admin_users')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_only_super_admin_can_delete_users(self):
        """Test only super admin can delete users"""
        user_to_delete = UserFactory()
        
        # Admin cannot delete
        self.client.force_authenticate(user=self.admin)
        url = reverse('accounts:admin_user_detail', kwargs={'pk': user_to_delete.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Super admin can delete
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=user_to_delete.id).exists())
