from rest_framework.test import APITestCase
from rest_framework import status

class AuthTests(APITestCase):
    def test_register_login(self):
        reg = self.client.post("/api/auth/register/", {"username":"u1","email":"u@e.com","password":"pass123","role":"seller"})
        self.assertEqual(reg.status_code, status.HTTP_201_CREATED)
        login = self.client.post("/api/auth/login/", {"username":"u1","password":"pass123"})
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertIn("token", login.data)
