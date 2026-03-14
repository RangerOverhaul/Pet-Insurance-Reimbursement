from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User


class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("auth-register")
        self.login_url = reverse("auth-login")
        self.me_url = reverse("auth-me")

    def _register(self, email="test@example.com", password="StrongPass123!", role="CUSTOMER"):
        return self.client.post(self.register_url, {
            "email": email,
            "password": password,
            "password2": password,
            "role": role,
        })

    def test_register_customer(self):
        res = self._register()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["role"], "CUSTOMER")

    def test_register_duplicate_email(self):
        self._register()
        res = self._register()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        res = self.client.post(self.register_url, {
            "email": "a@b.com",
            "password": "StrongPass123!",
            "password2": "WrongPass!",
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login(self):
        self._register()
        res = self.client.post(self.login_url, {
            "email": "test@example.com",
            "password": "StrongPass123!",
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_me_requires_auth(self):
        res = self.client.get(self.me_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user(self):
        self._register(email="me@example.com")
        login = self.client.post(self.login_url, {
            "email": "me@example.com",
            "password": "StrongPass123!",
        })
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        res = self.client.get(self.me_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], "me@example.com")