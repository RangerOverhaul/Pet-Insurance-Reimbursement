import io
from datetime import date, timedelta
from unittest.mock import patch
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from pets.models import Pet
from .models import Claim


def create_user(email, role="CUSTOMER", password="StrongPass123!"):
    return User.objects.create_user(email=email, password=password, role=role)


def get_token(client, email, password="StrongPass123!"):
    res = client.post(reverse("auth-login"), {"email": email, "password": password})
    return res.data["access"]


def create_pet(owner, name="Buddy"):
    return Pet.objects.create(
        owner=owner,
        name=name,
        species="DOG",
        birth_date=date(2020, 1, 1),
        coverage_start=date.today(),
    )


def make_invoice(content=b"invoice content", name="invoice.pdf"):
    return SimpleUploadedFile(name, content, content_type="application/pdf")


# Patch the async task globally so threads don't fight the test DB
@patch("claims.views.process_claim_async")
class ClaimTests(APITestCase):
    def setUp(self):
        self.customer = create_user("customer@test.com")
        self.other_customer = create_user("other@test.com")
        self.support = create_user("support@test.com", role="SUPPORT")

        self.token = get_token(self.client, "customer@test.com")
        self.other_token = get_token(self.client, "other@test.com")
        self.support_token = get_token(self.client, "support@test.com")

        self.pet = create_pet(self.customer)
        self.other_pet = create_pet(self.other_customer, "Max")

        self.list_url = reverse("claim-list")

    def auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def _claim_data(self, pet=None, offset_days=1):
        event_date = str(date.today() + timedelta(days=offset_days))
        return {
            "pet": (pet or self.pet).id,
            "invoice": make_invoice(),
            "invoice_date": event_date,
            "date_of_event": event_date,
            "amount": "150.00",
        }

    # ── Create ──────────────────────────────────────────────────────────────

    def test_customer_can_submit_claim(self, mock_task):
        self.auth(self.token)
        res = self.client.post(self.list_url, self._claim_data(), format="multipart")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["status"], Claim.Status.PROCESSING)
        mock_task.assert_called_once()

    def test_claim_starts_in_processing(self, mock_task):
        self.auth(self.token)
        res = self.client.post(self.list_url, self._claim_data(), format="multipart")
        self.assertEqual(res.data["status"], "PROCESSING")

    def test_duplicate_invoice_rejected(self, mock_task):
        self.auth(self.token)
        content = b"unique invoice bytes"
        data1 = {**self._claim_data(), "invoice": make_invoice(content, "inv1.pdf")}
        data2 = {**self._claim_data(), "invoice": make_invoice(content, "inv2.pdf")}
        self.client.post(self.list_url, data1, format="multipart")
        res = self.client.post(self.list_url, data2, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("duplicate", str(res.data).lower())

    def test_customer_cannot_claim_for_others_pet(self, mock_task):
        self.auth(self.token)
        data = self._claim_data(pet=self.other_pet)
        res = self.client.post(self.list_url, data, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_event_outside_coverage_rejected(self, mock_task):
        self.auth(self.token)
        bad_date = str(date.today() - timedelta(days=10))
        data = {**self._claim_data(), "date_of_event": bad_date, "invoice_date": bad_date}
        res = self.client.post(self.list_url, data, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Ownership visibility ────────────────────────────────────────────────

    def test_customer_sees_only_own_claims(self, mock_task):
        self.auth(self.token)
        self.client.post(self.list_url, self._claim_data(), format="multipart")
        self.auth(self.other_token)
        self.client.post(self.list_url, self._claim_data(pet=self.other_pet), format="multipart")
        self.auth(self.token)
        res = self.client.get(self.list_url)
        emails = [c["owner_email"] for c in res.data["results"]]
        self.assertTrue(all(e == "customer@test.com" for e in emails))

    def test_support_sees_all_claims(self, mock_task):
        self.auth(self.token)
        d1 = {**self._claim_data(), "invoice": make_invoice(b"claim-c1", "c1.pdf")}
        self.client.post(self.list_url, d1, format="multipart")
        self.auth(self.other_token)
        d2 = {**self._claim_data(pet=self.other_pet), "invoice": make_invoice(b"claim-c2", "c2.pdf")}
        self.client.post(self.list_url, d2, format="multipart")
        self.auth(self.support_token)
        res = self.client.get(self.list_url)
        self.assertEqual(res.data["count"], 2)

    # ── Review ──────────────────────────────────────────────────────────────

    def test_support_can_approve_in_review_claim(self, mock_task):
        claim = Claim.objects.create(
            owner=self.customer, pet=self.pet,
            invoice=make_invoice(b"reviewable"), invoice_hash="abc123",
            invoice_date=date.today() + timedelta(days=1),
            date_of_event=date.today() + timedelta(days=1),
            amount="200.00", status=Claim.Status.IN_REVIEW,
        )
        self.auth(self.support_token)
        url = reverse("claim-review", args=[claim.id])
        res = self.client.patch(url, {"status": "APPROVED", "review_notes": "All good"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        claim.refresh_from_db()
        self.assertEqual(claim.status, Claim.Status.APPROVED)

    def test_support_can_reject_in_review_claim(self, mock_task):
        claim = Claim.objects.create(
            owner=self.customer, pet=self.pet,
            invoice=make_invoice(b"rejectable"), invoice_hash="def456",
            invoice_date=date.today() + timedelta(days=1),
            date_of_event=date.today() + timedelta(days=1),
            amount="200.00", status=Claim.Status.IN_REVIEW,
        )
        self.auth(self.support_token)
        url = reverse("claim-review", args=[claim.id])
        res = self.client.patch(url, {"status": "REJECTED", "review_notes": "Invalid"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        claim.refresh_from_db()
        self.assertEqual(claim.status, Claim.Status.REJECTED)

    def test_customer_cannot_review_claim(self, mock_task):
        claim = Claim.objects.create(
            owner=self.customer, pet=self.pet,
            invoice=make_invoice(b"customer review"), invoice_hash="ghi789",
            invoice_date=date.today() + timedelta(days=1),
            date_of_event=date.today() + timedelta(days=1),
            amount="200.00", status=Claim.Status.IN_REVIEW,
        )
        self.auth(self.token)
        url = reverse("claim-review", args=[claim.id])
        res = self.client.patch(url, {"status": "APPROVED"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_review_non_in_review_claim(self, mock_task):
        claim = Claim.objects.create(
            owner=self.customer, pet=self.pet,
            invoice=make_invoice(b"processing claim"), invoice_hash="jkl012",
            invoice_date=date.today() + timedelta(days=1),
            date_of_event=date.today() + timedelta(days=1),
            amount="200.00", status=Claim.Status.PROCESSING,
        )
        self.auth(self.support_token)
        url = reverse("claim-review", args=[claim.id])
        res = self.client.patch(url, {"status": "APPROVED"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Pending review list ──────────────────────────────────────────────────

    def test_pending_review_endpoint_returns_in_review_claims(self, mock_task):
        Claim.objects.create(
            owner=self.customer, pet=self.pet,
            invoice=make_invoice(b"pending1"), invoice_hash="p1",
            invoice_date=date.today() + timedelta(days=1),
            date_of_event=date.today() + timedelta(days=1),
            amount="100.00", status=Claim.Status.IN_REVIEW,
        )
        Claim.objects.create(
            owner=self.customer, pet=self.pet,
            invoice=make_invoice(b"pending2"), invoice_hash="p2",
            invoice_date=date.today() + timedelta(days=2),
            date_of_event=date.today() + timedelta(days=2),
            amount="200.00", status=Claim.Status.PROCESSING,
        )
        self.auth(self.support_token)
        url = reverse("claim-pending-review")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["status"], "IN_REVIEW")

    def test_async_task_called_on_claim_create(self, mock_task):
        self.auth(self.token)
        self.client.post(self.list_url, self._claim_data(), format="multipart")
        self.assertTrue(mock_task.called)