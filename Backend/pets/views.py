from rest_framework import viewsets, permissions
from .models import Pet
from .serializers import PetSerializer
from .permissions import IsOwnerOrSupportOrAdmin
from users.models import User


class PetViewSet(viewsets.ModelViewSet):
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrSupportOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role in [User.Role.SUPPORT, User.Role.ADMIN]:
            return Pet.objects.select_related("owner").all().order_by("-created_at")
        return Pet.objects.filter(owner=user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)