from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Product, Category

User = get_user_model()

class ProductAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="seller", password="pass123", role="seller")
        self.category = Category.objects.create(name="Phones", slug="phones")
        self.client.force_authenticate(self.user)

    def test_create_product(self):
        data = {"title": "iPhone", "description": "Good", "price": "1000.00", "stock": 5, "category": self.category.id}
        url = "/api/products/"
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)

    def test_list_products(self):
        Product.objects.create(title="Laptop", description="", price="2000.00", stock=2, seller=self.user, category=self.category)
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
