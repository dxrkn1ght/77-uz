from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Product

User = get_user_model()

class ProductAPITest(APITestCase):
    def setUp(self):
        self.seller = User.objects.create_user(username="seller", password="pass123", role="seller")
        self.client.login(username="seller", password="pass123")

    def test_create_product(self):
        data = {"name": "Phone", "description": "New phone", "price": "1000.00"}
        response = self.client.post("/api/products/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)

    def test_list_products(self):
        Product.objects.create(name="Laptop", price=2000, seller=self.seller)
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
