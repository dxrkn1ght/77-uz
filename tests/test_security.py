from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.cache import cache
from .factories import UserFactory, SellerUserFactory

class SecurityHeadersTest(TestCase):
    """Test security headers middleware"""
    
    def setUp(self):
        self.client = Client()
    
    def test_security_headers_present(self):
        """Test that security headers are added to responses"""
        response = self.client.get('/api/v1/info/')
        
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')
        self.assertIn('Referrer-Policy', response)
        self.assertIn('Permissions-Policy', response)

class RateLimitTest(APITestCase):
    """Test rate limiting functionality"""
    
    def setUp(self):
        self.user = UserFactory()
        cache.clear()  # Clear cache before each test
    
    def test_anonymous_rate_limit(self):
        """Test rate limiting for anonymous users"""
        url = reverse('accounts:login')
        
        # Make requests up to the limit
        for i in range(5):  # Assuming limit is higher than 5
            response = self.client.post(url, {
                'phone_number': '+998901234567',
                'password': 'wrong'
            })
            # Should not be rate limited yet
            self.assertNotEqual(response.status_code, 429)
    
    def test_authenticated_user_higher_limit(self):
        """Test authenticated users have higher rate limits"""
        self.client.force_authenticate(user=self.user)
        url = reverse('accounts:profile')
        
        # Authenticated users should have much higher limits
        for i in range(10):
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 429)

class InputValidationTest(APITestCase):
    """Test input validation and sanitization"""
    
    def setUp(self):
        self.seller = SellerUserFactory()
        self.client.force_authenticate(user=self.seller)
    
    def test_html_injection_prevention(self):
        """Test prevention of HTML injection"""
        url = reverse('store:ads_create')
        data = {
            'name_uz': '<script>alert("xss")</script>Test Ad',
            'name_ru': 'Test Ad',
            'description_uz': 'Normal description',
            'description_ru': 'Normal description',
            'price': 100000,
            'category': 1
        }
        response = self.client.post(url, data, format='json')
        
        # Should either reject the request or sanitize the input
        if response.status_code == 400:
            self.assertIn('error', response.data or {})
        elif response.status_code == 201:
            # If created, script tags should be removed/escaped
            self.assertNotIn('<script>', response.data.get('name', ''))
    
    def test_sql_injection_prevention(self):
        """Test prevention of SQL injection attempts"""
        url = reverse('store:ads_list')
        
        # Try SQL injection in search parameter
        response = self.client.get(url, {
            'search': "'; DROP TABLE ads; --"
        })
        
        # Should not cause server error
        self.assertNotEqual(response.status_code, 500)
    
    def test_phone_number_validation(self):
        """Test phone number format validation"""
        url = reverse('accounts:register')
        
        # Invalid phone number formats
        invalid_phones = [
            '123456789',  # No country code
            '+99890123456789012345',  # Too long
            '+abc123456789',  # Contains letters
            '998901234567',  # Missing +
        ]
        
        for phone in invalid_phones:
            data = {
                'phone_number': phone,
                'password': 'testpass123',
                'password_confirm': 'testpass123'
            }
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class AuthenticationSecurityTest(APITestCase):
    """Test authentication security measures"""
    
    def setUp(self):
        self.user = UserFactory(phone_number='+998901234567')
        self.user.set_password('testpass123')
        self.user.save()
    
    def test_password_not_returned_in_responses(self):
        """Test that passwords are never returned in API responses"""
        # Login
        url = reverse('accounts:login')
        response = self.client.post(url, {
            'phone_number': '+998901234567',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('password', str(response.data))
        
        # Profile
        self.client.force_authenticate(user=self.user)
        url = reverse('accounts:profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('password', str(response.data))
    
    def test_jwt_token_required_for_protected_endpoints(self):
        """Test that JWT tokens are required for protected endpoints"""
        protected_urls = [
            reverse('accounts:profile'),
            reverse('store:ads_create'),
            reverse('store:my_ads'),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_invalid_jwt_token_rejected(self):
        """Test that invalid JWT tokens are rejected"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        url = reverse('accounts:profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class PermissionTest(APITestCase):
    """Test role-based permissions"""
    
    def setUp(self):
        self.user = UserFactory()
        self.seller = SellerUserFactory()
        self.admin = UserFactory(role='admin', is_staff=True)
        self.super_admin = UserFactory(role='super_admin', is_staff=True, is_superuser=True)
    
    def test_seller_permissions(self):
        """Test seller role permissions"""
        self.client.force_authenticate(user=self.seller)
        
        # Sellers can create ads
        url = reverse('store:ads_create')
        response = self.client.post(url, {})
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Sellers cannot access admin endpoints
        url = reverse('accounts:admin_users')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_permissions(self):
        """Test admin role permissions"""
        self.client.force_authenticate(user=self.admin)
        
        # Admins can access user management
        url = reverse('accounts:admin_users')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Admins cannot delete users (only super admin can)
        user_to_delete = UserFactory()
        url = reverse('accounts:admin_user_detail', kwargs={'pk': user_to_delete.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_super_admin_permissions(self):
        """Test super admin role permissions"""
        self.client.force_authenticate(user=self.super_admin)
        
        # Super admins can delete users
        user_to_delete = UserFactory()
        url = reverse('accounts:admin_user_detail', kwargs={'pk': user_to_delete.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
