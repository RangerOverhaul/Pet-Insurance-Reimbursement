import hashlib
from django.db import models
from users.models import User
from pets.models import Pet


def invoice_upload_path(instance, filename):
    return f"invoices/{instance.owner.id}/{filename}"


class Claim(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Submitted"
        PROCESSING = "PROCESSING", "Processing"
        IN_REVIEW = "IN_REVIEW", "In Review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="claims")
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="claims")
    invoice = models.FileField(upload_to=invoice_upload_path)
    invoice_hash = models.CharField(max_length=64, unique=True, editable=False)
    invoice_date = models.DateField()
    date_of_event = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    review_notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.invoice and not self.invoice_hash:
            self.invoice_hash = self._compute_invoice_hash()
        super().save(*args, **kwargs)

    def _compute_invoice_hash(self):
        hasher = hashlib.sha256()
        for chunk in self.invoice.chunks():
            hasher.update(chunk)
        return hasher.hexdigest()

    def __str__(self):
        return f"Claim #{self.id} — {self.pet.name} ({self.status})"