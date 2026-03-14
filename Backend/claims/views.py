from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Claim
from .serializers import ClaimSerializer, ClaimReviewSerializer
from .permissions import IsClaimOwnerOrStaff, IsSupportOrAdmin
from .tasks import process_claim_async
from users.models import User


class ClaimViewSet(viewsets.ModelViewSet):
    serializer_class = ClaimSerializer
    permission_classes = [permissions.IsAuthenticated, IsClaimOwnerOrStaff]

    def get_queryset(self):
        user = self.request.user
        qs = Claim.objects.select_related("owner", "pet").order_by("-created_at")
        if user.role in [User.Role.SUPPORT, User.Role.ADMIN]:
            status_filter = self.request.query_params.get("status")
            if status_filter:
                qs = qs.filter(status=status_filter)
            return qs
        return qs.filter(owner=user)

    def perform_create(self, serializer):
        claim = serializer.save(owner=self.request.user, status=Claim.Status.PROCESSING)
        process_claim_async(claim.id)

    def update(self, request, *args, **kwargs):
        if request.user.role == User.Role.CUSTOMER:
            return Response(
                {"detail": "Customers cannot update claims."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        claim = self.get_object()
        if claim.status not in [Claim.Status.SUBMITTED, Claim.Status.REJECTED]:
            return Response(
                {"detail": "Only SUBMITTED or REJECTED claims can be deleted."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[permissions.IsAuthenticated, IsSupportOrAdmin],
        url_path="review",
    )
    def review(self, request, pk=None):
        """
        PATCH /api/claims/{id}/review/
        Support/Admin: approve or reject a claim that is IN_REVIEW.
        """
        claim = self.get_object()
        serializer = ClaimReviewSerializer(claim, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ClaimSerializer(claim).data)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated, IsSupportOrAdmin],
        url_path="pending-review",
    )
    def pending_review(self, request):
        """
        GET /api/claims/pending-review/
        Returns all claims with status IN_REVIEW for the support team.
        """
        claims = (
            Claim.objects.filter(status=Claim.Status.IN_REVIEW)
            .select_related("owner", "pet")
            .order_by("-created_at")
        )
        serializer = ClaimSerializer(claims, many=True)
        return Response(serializer.data)