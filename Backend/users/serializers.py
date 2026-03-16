from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "password2"]  # ← sin "role"

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(role=User.Role.CUSTOMER, **validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user model."""
    class Meta:
        model = User
        fields = ["id", "email", "role", "date_joined"]
        read_only_fields = ["id", "date_joined"]