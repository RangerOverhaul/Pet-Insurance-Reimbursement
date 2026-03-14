from datetime import date, timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from .models import Pet


def create_user(email, role="CUSTOMER", password="StrongPass123!"):
    return User.objects.create_user(email=email, password=password, role=role)


def get_token(client, email, password="StrongPass123!"):
    res = client.post(reverse("auth-login"), {"email": email, "password": password})
    return res.data["access"]


class PetTests(APITestCase):
    def setUp(self):
        self.customer = create_user("customer@test.com")
        self.other_customer = create_user("other@test.com")
        self.support = create_user("support@test.com", role="SUPPORT")

        self.token = get_token(self.client, "customer@test.com")
        self.other_token = get_token(self.client, "other@test.com")
        self.support_token = get_token(self.client, "support@test.com")

        self.list_url = reverse("pet-list")

        self.pet_data = {
            "name": "Buddy",
            "species": "DOG",
            "birth_date": "2020-01-01",
            "coverage_start": str(date.today()),
        }

    def auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def create_pet(self, token=None):
        self.auth(token or self.token)
        return self.client.post(self.list_url, self.pet_data)

    # ── Create ──────────────────────────────────────────────────────────────

    def test_customer_can_create_pet(self):
        res = self.create_pet()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["name"], "Buddy")

    def test_coverage_end_auto_computed(self):
        res = self.create_pet()
        expected = str(date.today() + timedelta(days=365))
        self.assertEqual(res.data["coverage_end"], expected)

    def test_unauthenticated_cannot_create(self):
        res = self.client.post(self.list_url, self.pet_data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_future_birth_date_rejected(self):
        self.auth(self.token)
        data = {**self.pet_data, "birth_date": str(date.today() + timedelta(days=10))}
        res = self.client.post(self.list_url, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # ── List / ownership ────────────────────────────────────────────────────

    def test_customer_sees_only_own_pets(self):
        self.create_pet(self.token)
        self.create_pet(self.other_token)
        self.auth(self.token)
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        emails = [p["owner_email"] for p in res.data["results"]]
        self.assertTrue(all(e == "customer@test.com" for e in emails))

    def test_support_sees_all_pets(self):
        self.create_pet(self.token)
        self.create_pet(self.other_token)
        self.auth(self.support_token)
        res = self.client.get(self.list_url)
        self.assertEqual(res.data["count"], 2)

    # ── Delete ──────────────────────────────────────────────────────────────

    def test_customer_cannot_delete_others_pet(self):
        res = self.create_pet(self.other_token)
        pet_id = res.data["id"]
        self.auth(self.token)
        res = self.client.delete(reverse("pet-detail", args=[pet_id]))
        self.assertIn(res.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])