from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from accounts.permissions import IsAdminPanelUser
from career.selectors import (
    get_admin_career_opportunities,
    get_admin_career_resource_configurations,
    get_public_career_opportunities,
)
from career.serializers import (
    CareerOpportunitySerializer,
    CareerResourceConfigurationSerializer,
    CareerResourcePayloadSerializer,
    PublicCareerOpportunitySerializer,
)
from career.services import get_active_career_resources_or_404
from core.mixins import AdminCrudEndpointMixin, PublicReadOnlyEndpointMixin
from core.responses import success_response


class PublicCareerOpportunityViewSet(PublicReadOnlyEndpointMixin):
    serializer_class = PublicCareerOpportunitySerializer
    permission_classes = [AllowAny]
    search_fields = ("title", "organization", "description")
    ordering_fields = ("title", "organization", "closes_at", "created_at")
    ordering = ("title",)

    def get_queryset(self):
        return get_public_career_opportunities()


class PublicCareerResourcesView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CareerResourcePayloadSerializer

    def get(self, request):
        configuration = get_active_career_resources_or_404()
        serializer = CareerResourcePayloadSerializer(configuration, context={"request": request})
        return success_response(serializer.data, message="Career resources retrieved successfully")


class AdminCareerOpportunityViewSet(AdminCrudEndpointMixin):
    serializer_class = CareerOpportunitySerializer
    permission_classes = [IsAdminPanelUser]
    filterset_fields = ("is_published",)
    search_fields = ("title", "organization", "description")
    ordering_fields = ("title", "organization", "closes_at", "created_at", "updated_at")
    ordering = ("title",)

    def get_queryset(self):
        return get_admin_career_opportunities()


class AdminCareerResourceConfigurationViewSet(AdminCrudEndpointMixin):
    serializer_class = CareerResourceConfigurationSerializer
    permission_classes = [IsAdminPanelUser]
    filterset_fields = ("is_active",)
    ordering_fields = ("updated_at", "created_at")
    ordering = ("-updated_at",)

    def get_queryset(self):
        return get_admin_career_resource_configurations()
