from rest_framework import serializers
from .models import Claim
from pets.models import Pet


class ClaimSerializer(serializers.ModelSerializer):
    pet_name = serializers.CharField(source="pet.name", read_only=True)
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Claim
        fields = [
            "id", "owner", "owner_email", "pet", "pet_name",
            "invoice", "invoice_date", "date_of_event",
            "amount", "status", "review_notes",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "owner", "status", "review_notes", "created_at", "updated_at"]

    def validate(self, attrs):
        request = self.context["request"]
        pet: Pet = attrs.get("pet") or (self.instance.pet if self.instance else None)

        # Ownership: customer can only claim for their own pets
        if pet and pet.owner != request.user:
            raise serializers.ValidationError({"pet": "You do not own this pet."})

        # Validate date_of_event within coverage
        date_of_event = attrs.get("date_of_event")
        if pet and date_of_event and not pet.is_date_covered(date_of_event):
            raise serializers.ValidationError(
                {"date_of_event": "Date of event is outside the pet's coverage period."}
            )

        # Validate invoice_date within coverage
        invoice_date = attrs.get("invoice_date")
        if pet and invoice_date and not pet.is_date_covered(invoice_date):
            raise serializers.ValidationError(
                {"invoice_date": "Invoice date is outside the pet's coverage period."}
            )

        return attrs

    def validate_invoice(self, value):
        """Compute hash and check for duplicates before saving."""
        import hashlib
        hasher = hashlib.sha256()
        for chunk in value.chunks():
            hasher.update(chunk)
        file_hash = hasher.hexdigest()

        # Seek back so model.save() can read the file again
        value.seek(0)

        if Claim.objects.filter(invoice_hash=file_hash).exists():
            raise serializers.ValidationError(
                "This invoice has already been submitted (duplicate file detected)."
            )

        # Attach hash to value for use in model.save()
        value._computed_hash = file_hash
        return value

    def create(self, validated_data):
        invoice = validated_data["invoice"]
        claim = super().create(validated_data)
        # Assign the pre-computed hash to avoid double-hashing
        if hasattr(invoice, "_computed_hash"):
            claim.invoice_hash = invoice._computed_hash
            claim.save(update_fields=["invoice_hash"])
        return claim


class ClaimReviewSerializer(serializers.ModelSerializer):
    """Used by SUPPORT/ADMIN to approve or reject a claim."""

    class Meta:
        model = Claim
        fields = ["status", "review_notes"]

    def validate_status(self, value):
        allowed = [Claim.Status.APPROVED, Claim.Status.REJECTED]
        if value not in allowed:
            raise serializers.ValidationError(
                f"Status must be one of: {[s.value for s in allowed]}"
            )
        return value

    def validate(self, attrs):
        if self.instance and self.instance.status != Claim.Status.IN_REVIEW:
            raise serializers.ValidationError(
                "Only claims with status IN_REVIEW can be reviewed."
            )
        return attrs