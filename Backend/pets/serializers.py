from rest_framework import serializers
from .models import Pet
from users.models import User
from datetime import timedelta

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

    def validate(self, attrs):
        request = self.context.get("request")
        if request and not self.instance:
            from django.utils import timezone
            coverage_start = attrs.get("coverage_start")
            if request.user.role == User.Role.CUSTOMER and coverage_start:
                if coverage_start  < (timezone.now().date() - timedelta(days=1)):
                    raise serializers.ValidationError(
                        {"coverage_start": "Coverage start date cannot be in the past."}
                    )
        return attrs
    