from rest_framework import serializers
from .models import Pet


class PetSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    is_coverage_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Pet
        fields = [
            "id", "owner", "owner_email", "name", "species",
            "birth_date", "coverage_start", "coverage_end",
            "is_coverage_active", "created_at",
        ]
        read_only_fields = ["id", "owner", "coverage_end", "created_at"]

    def validate_birth_date(self, value):
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError("Birth date cannot be in the future.")
        return value

    def validate_coverage_start(self, value):
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError("Coverage start date cannot be in the past.")
        return value