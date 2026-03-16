from rest_framework import serializers
from .models import Claim, BANK_CHOICES
from pets.models import Pet


class ClaimSerializer(serializers.ModelSerializer):
    pet_name = serializers.CharField(source="pet.name", read_only=True)
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    owner_full_name = serializers.CharField(source="owner.full_name", read_only=True)
    owner_document = serializers.CharField(source="owner.document_number", read_only=True)
    owner_phone = serializers.CharField(source="owner.phone_number", read_only=True)
    bank_display = serializers.CharField(source="get_bank_display", read_only=True)
    reviewed_by_email = serializers.SerializerMethodField()

    class Meta:
        model = Claim
        fields = [
            "id", "owner", "owner_email", "owner_full_name", "owner_document", "owner_phone",
            "pet", "pet_name",
            "invoice", "invoice_date", "date_of_event", "amount",
            "bank", "bank_display", "account_number",
            "status", "review_notes", "reviewed_by", "reviewed_by_email",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "owner", "status", "review_notes",
            "reviewed_by", "created_at", "updated_at",
        ]

    def get_reviewed_by_email(self, obj):
        if obj.reviewed_by:
            return obj.reviewed_by.email
        return None

    def validate(self, attrs):
        request = self.context["request"]
        pet: Pet = attrs.get("pet") or (self.instance.pet if self.instance else None)

        if pet and pet.owner != request.user:
            raise serializers.ValidationError({"pet": "You do not own this pet."})

        date_of_event = attrs.get("date_of_event")
        if pet and date_of_event and not pet.is_date_covered(date_of_event):
            raise serializers.ValidationError(
                {"date_of_event": "Date of event is outside the pet's coverage period."}
            )

        invoice_date = attrs.get("invoice_date")
        if pet and invoice_date and not pet.is_date_covered(invoice_date):
            raise serializers.ValidationError(
                {"invoice_date": "Invoice date is outside the pet's coverage period."}
            )

        return attrs

    def validate_invoice(self, value):
        import hashlib
        hasher = hashlib.sha256()
        for chunk in value.chunks():
            hasher.update(chunk)
        file_hash = hasher.hexdigest()
        value.seek(0)

        if Claim.objects.filter(invoice_hash=file_hash).exists():
            raise serializers.ValidationError(
                "This invoice has already been submitted (duplicate file detected)."
            )

        value._computed_hash = file_hash
        return value

    def create(self, validated_data):
        invoice = validated_data["invoice"]
        claim = super().create(validated_data)
        if hasattr(invoice, "_computed_hash"):
            claim.invoice_hash = invoice._computed_hash
            claim.save(update_fields=["invoice_hash"])
        return claim


class ClaimReviewSerializer(serializers.ModelSerializer):
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