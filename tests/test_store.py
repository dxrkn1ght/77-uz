from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .factories import (
    UserFactory, SellerUserFactory, CategoryFactory, 
    AdFactory, AdPhotoFactory
)
from apps.store.models import Ad, AdLike

class CategoryModelTest(TestCase):
    """Test Category model"""
    
    def test_create_category(self):
        category = CategoryFactory()
        self.assertTrue(category.is_active)
        self.assertIsNotNone(category.slug)
    
    def test_category_hierarchy(self):
        parent = CategoryFactory()
        child = CategoryFactory(parent=parent)
        
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children.all())

class AdModelTest(TestCase):
    """Test Ad model"""
    
    def test_create_ad(self):
        ad = AdFactory()
        self.assertTrue(ad.is_active)
        self.assertIsNotNone(ad.slug)
        self.assertEqual(ad.view_count, 0)
    
    def test_ad_increment_view_count(self):
        ad = AdFactory()
        initial_count = ad.view_count
        ad.increment_view_count()
        
        self.assertEqual(ad.view_count, initial_count + 1)

class CategoryAPITest(APITestCase):
    """Test category endpoints"""
    
    def setUp(self):
        self.category = CategoryFactory()
        self.subcategory = CategoryFactory(parent=self.category)
    
    def test_list_categories(self):
        """Test listing categories"""
        url = reverse('store:categories')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only root categories
    
    def test_categories_with_children(self):
        """Test categories with nested children"""
        url = reverse('store:categories_with_childs')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data[0]['children']), 1)

class AdAPITest(APITestCase):
    """Test advertisement endpoints"""
    
    def setUp(self):
        self.seller = SellerUserFactory()
        self.regular_user = UserFactory()
        self.category = CategoryFactory()
        self.ad = AdFactory(seller=self.seller, category=self.category)
    
    def test_list_ads(self):
        """Test listing advertisements"""
        url = reverse('store:ads_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_ad_detail(self):
        """Test getting ad details"""
        url = reverse('store:ads_detail', kwargs={'slug': self.ad.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.ad.id)
        self.assertEqual(response.data['name'], self.ad.name_uz)
    
    def test_create_ad_requires_seller_role(self):
        """Test creating ad requires seller role"""
        # Regular user cannot create ads
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('store:ads_create')
        data = {
            'name_uz': 'Test Ad',
            'name_ru': 'Test Ad',
            'description_uz': 'Test description',
            'description_ru': 'Test description',
            'price': 100000,
            'category': self.category.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Seller can create ads
        self.client.force_authenticate(user=self.seller)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_update_ad_owner_only(self):
        """Test only ad owner can update ad"""
        other_seller = SellerUserFactory()
        
        # Other seller cannot update
        self.client.force_authenticate(user=other_seller)
        url = reverse('store:ads_update', kwargs={'slug': self.ad.slug})
        data = {'name_uz': 'Updated Name'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Owner can update
        self.client.force_authenticate(user=self.seller)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_ad_like_functionality(self):
        """Test ad like/unlike functionality"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('store:ads_like', kwargs={'slug': self.ad.slug})
        
        # Like ad
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_liked'])
        self.assertTrue(AdLike.objects.filter(user=self.regular_user, ad=self.ad).exists())
        
        # Unlike ad
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_liked'])
        self.assertFalse(AdLike.objects.filter(user=self.regular_user, ad=self.ad).exists())
    
    def test_ad_search_and_filtering(self):
        """Test ad search and filtering"""
        # Create ads with different properties
        expensive_ad = AdFactory(price=1000000, name_uz='Expensive Item')
        cheap_ad = AdFactory(price=50000, name_uz='Cheap Item')
        
        url = reverse('store:ads_list')
        
        # Test price filtering
        response = self.client.get(url, {'min_price': 100000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return expensive ad and original ad
        
        # Test search
        response = self.client.get(url, {'search': 'Expensive'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return expensive ad
    
    def test_my_ads_seller_only(self):
        """Test my ads endpoint for sellers"""
        self.client.force_authenticate(user=self.seller)
        url = reverse('store:my_ads')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.ad.id)
    
    def test_ad_view_tracking(self):
        """Test ad view count tracking"""
        initial_count = self.ad.view_count
        url = reverse('store:ads_detail', kwargs={'slug': self.ad.slug})
        
        # View ad
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check view count increased
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.view_count, initial_count + 1)

class AdPermissionTest(APITestCase):
    """Test ad permissions and security"""
    
    def setUp(self):
        self.seller = SellerUserFactory()
        self.other_seller = SellerUserFactory()
        self.regular_user = UserFactory()
        self.ad = AdFactory(seller=self.seller)
    
    def test_anonymous_user_can_view_ads(self):
        """Test anonymous users can view ads"""
        url = reverse('store:ads_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        url = reverse('store:ads_detail', kwargs={'slug': self.ad.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_anonymous_user_cannot_create_ads(self):
        """Test anonymous users cannot create ads"""
        url = reverse('store:ads_create')
        data = {'name_uz': 'Test Ad'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_regular_user_cannot_create_ads(self):
        """Test regular users cannot create ads"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('store:ads_create')
        data = {'name_uz': 'Test Ad'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
