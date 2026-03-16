from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User


class AuthTests(APITestCase):
    """Tests for the authentication views."""
    
    def setUp(self):
        self.register_url = reverse("auth-register")
        self.login_url = reverse("auth-login")
        self.me_url = reverse("auth-me")

    def _register(self, email="test@example.com", password="StrongPass123!", role="CUSTOMER"):
        """Helper method to register a user."""
        return self.client.post(self.register_url, {
            "email": email,
            "password": password,
            "password_confirm": password,
            "role": role,
        })

    def test_register_customer(self):
        """Test registering a new customer."""
        res = self._register()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["role"], "CUSTOMER")

    def test_register_duplicate_email(self):
        """Test registering a duplicate email."""
        self._register()
        res = self._register()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        """Test registering a user with a password mismatch."""
        res = self.client.post(self.register_url, {
            "email": "a@b.com",
            "password": "StrongPass123!",
            "password_confirm": "WrongPass!",
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login(self):
        """Test logging in a user."""
        self._register()
        res = self.client.post(self.login_url, {
            "email": "test@example.com",
            "password": "StrongPass123!",
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_me_requires_auth(self):
        """Test that the me endpoint requires authentication."""
        res = self.client.get(self.me_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user(self):
        """Test that the me endpoint returns the current user."""
        self._register(email="me@example.com")
        login = self.client.post(self.login_url, {
            "email": "me@example.com",
            "password": "StrongPass123!",
        })
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        res = self.client.get(self.me_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], "me@example.com")