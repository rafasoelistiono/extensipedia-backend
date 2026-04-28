from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from accounts.permissions import IsAdminPanelUser
from advocacy.selectors import (
    get_admin_advocacy_campaigns,
    get_admin_advocacy_policy_resource_configurations,
    get_public_advocacy_campaigns,
)
from advocacy.serializers import (
    AdvocacyCampaignSerializer,
    AdvocacyPolicyResourceConfigurationSerializer,
    AdvocacyPolicyResourcePayloadSerializer,
    PublicAdvocacyCampaignSerializer,
)
from advocacy.services import get_active_advocacy_policy_resources_or_404
from core.mixins import AdminCrudEndpointMixin, PublicReadOnlyEndpointMixin
from core.responses import success_response


class PublicAdvocacyCampaignViewSet(PublicReadOnlyEndpointMixin):
    serializer_class = PublicAdvocacyCampaignSerializer
    permission_classes = [AllowAny]
    search_fields = ("title", "summary", "content", "slug")
    ordering_fields = ("title", "created_at", "updated_at")
    ordering = ("title",)

    def get_queryset(self):
        return get_public_advocacy_campaigns()


class PublicAdvocacyPolicyResourcesView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AdvocacyPolicyResourcePayloadSerializer

    def get(self, request):
        configuration = get_active_advocacy_policy_resources_or_404()
        serializer = AdvocacyPolicyResourcePayloadSerializer(configuration, context={"request": request})
        return success_response(serializer.data, message="Advocacy policy resources retrieved successfully")


class AdminAdvocacyCampaignViewSet(AdminCrudEndpointMixin):
    serializer_class = AdvocacyCampaignSerializer
    permission_classes = [IsAdminPanelUser]
    filterset_fields = ("is_published",)
    search_fields = ("title", "summary", "content", "slug")
    ordering_fields = ("title", "created_at", "updated_at")
    ordering = ("title",)

    def get_queryset(self):
        return get_admin_advocacy_campaigns()


class AdminAdvocacyPolicyResourceConfigurationViewSet(AdminCrudEndpointMixin):
    serializer_class = AdvocacyPolicyResourceConfigurationSerializer
    permission_classes = [IsAdminPanelUser]
    filterset_fields = ("is_active",)
    ordering_fields = ("updated_at", "created_at")
    ordering = ("-updated_at",)

    def get_queryset(self):
        return get_admin_advocacy_policy_resource_configurations()
