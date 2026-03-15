from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from accounts.permissions import IsAdminPanelUser
from aspirations.models import AspirationSubmission
from aspirations.selectors import (
    get_admin_aspiration_submissions,
    get_featured_aspirations,
)
from aspirations.serializers import (
    AdminAspirationDetailSerializer,
    AdminAspirationListSerializer,
    PublicAspirationSubmitSerializer,
    PublicFeaturedAspirationSerializer,
    PublicTrackingSerializer,
    SetFeaturedSerializer,
)
from aspirations.services import (
    create_public_aspiration_submission,
    get_ticket_for_public_tracking,
    increment_upvote,
    increment_vote,
    set_featured_state,
    update_aspiration_submission,
)
from aspirations.throttles import (
    PublicAspirationInteractionBurstThrottle,
    PublicAspirationInteractionSustainedThrottle,
    PublicAspirationSubmitBurstThrottle,
    PublicAspirationSubmitSustainedThrottle,
    PublicTicketTrackingThrottle,
)
from core.responses import success_response


class PublicAspirationSubmitView(generics.GenericAPIView):
    serializer_class = PublicAspirationSubmitSerializer
    permission_classes = [AllowAny]
    throttle_classes = [PublicAspirationSubmitBurstThrottle, PublicAspirationSubmitSustainedThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        aspiration = create_public_aspiration_submission(**serializer.validated_data)
        data = PublicTrackingSerializer(aspiration, context={"request": request}).data
        return success_response(data, message="Aspiration submitted successfully", status_code=status.HTTP_201_CREATED)


class PublicFeaturedAspirationView(generics.ListAPIView):
    serializer_class = PublicFeaturedAspirationSerializer
    permission_classes = [AllowAny]
    ordering = ("-updated_at", "-created_at")

    def get_queryset(self):
        return get_featured_aspirations(self.request.query_params.get("visibility"))

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True, context={"request": request})
        return success_response(serializer.data, message="Featured aspirations retrieved successfully")


class PublicAspirationUpvoteView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PublicAspirationInteractionBurstThrottle, PublicAspirationInteractionSustainedThrottle]
    serializer_class = PublicFeaturedAspirationSerializer

    def post(self, request, pk):
        aspiration = generics.get_object_or_404(
            AspirationSubmission,
            pk=pk,
            is_featured=True,
            status__in=[AspirationSubmission.Status.INVESTIGATING, AspirationSubmission.Status.RESOLVED],
        )
        aspiration = increment_upvote(aspiration)
        serializer = PublicFeaturedAspirationSerializer(aspiration, context={"request": request})
        return success_response(serializer.data, message="Aspiration upvoted successfully")


class PublicAspirationVoteView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PublicAspirationInteractionBurstThrottle, PublicAspirationInteractionSustainedThrottle]
    serializer_class = PublicFeaturedAspirationSerializer

    def post(self, request, pk):
        aspiration = generics.get_object_or_404(
            AspirationSubmission,
            pk=pk,
            is_featured=True,
            status__in=[AspirationSubmission.Status.INVESTIGATING, AspirationSubmission.Status.RESOLVED],
        )
        aspiration = increment_vote(aspiration)
        serializer = PublicFeaturedAspirationSerializer(aspiration, context={"request": request})
        return success_response(serializer.data, message="Aspiration vote recorded successfully")


class PublicTicketTrackingView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PublicTicketTrackingThrottle]
    serializer_class = PublicTrackingSerializer

    def get(self, request):
        ticket_id = request.query_params.get("ticket_id")
        if not ticket_id:
            return success_response(
                data={
                    "ticket_id": None,
                    "title": None,
                    "status": None,
                    "submitted_at": None,
                    "updated_at": None,
                    "visibility": None,
                    "short_description": None,
                },
                message="Search a ticket ID to view aspiration progress.",
            )

        aspiration = get_ticket_for_public_tracking(ticket_id)
        serializer = PublicTrackingSerializer(aspiration, context={"request": request})
        return success_response(serializer.data, message="Ticket tracking retrieved successfully")


class AdminAspirationSubmissionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminPanelUser]
    http_method_names = ["get", "patch", "post", "head", "options"]
    filterset_fields = ("status", "visibility", "is_featured")
    search_fields = ("ticket_id", "title", "full_name", "email", "npm")
    ordering_fields = ("created_at", "updated_at", "status", "ticket_id", "is_featured")
    ordering = ("-created_at",)

    def get_queryset(self):
        return get_admin_aspiration_submissions()

    def get_serializer_class(self):
        if self.action == "list":
            return AdminAspirationListSerializer
        if self.action in {"set_featured", "unset_featured"}:
            return SetFeaturedSerializer
        return AdminAspirationDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={"request": request})
            response = self.get_paginated_response(serializer.data)
            response._message = "Aspiration submissions retrieved successfully"
            return response

        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        return success_response(serializer.data, message="Aspiration submissions retrieved successfully")

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), context={"request": request})
        return success_response(serializer.data, message="Aspiration submission retrieved successfully")

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        aspiration = update_aspiration_submission(instance, serializer.validated_data, request.user)
        detail_serializer = AdminAspirationDetailSerializer(aspiration, context={"request": request})
        return success_response(detail_serializer.data, message="Aspiration submission updated successfully")

    @action(detail=True, methods=["post"], url_path="set-featured")
    def set_featured(self, request, pk=None):
        aspiration = self.get_object()
        serializer = self.get_serializer(data={}, context={"aspiration": aspiration})
        serializer.is_valid(raise_exception=True)
        aspiration.updated_by = request.user
        aspiration = set_featured_state(aspiration, is_featured=True)
        detail_serializer = AdminAspirationDetailSerializer(aspiration, context={"request": request})
        return success_response(detail_serializer.data, message="Aspiration marked as featured successfully")

    @action(detail=True, methods=["post"], url_path="unset-featured")
    def unset_featured(self, request, pk=None):
        aspiration = self.get_object()
        aspiration.updated_by = request.user
        aspiration = set_featured_state(aspiration, is_featured=False)
        detail_serializer = AdminAspirationDetailSerializer(aspiration, context={"request": request})
        return success_response(detail_serializer.data, message="Aspiration unfeatured successfully")
