from rest_framework.permissions import AllowAny

from accounts.permissions import IsAdminPanelUser
from advocacy.selectors import get_admin_advocacy_campaigns, get_public_advocacy_campaigns
from advocacy.serializers import AdvocacyCampaignSerializer, PublicAdvocacyCampaignSerializer
from core.mixins import AdminCrudEndpointMixin, PublicReadOnlyEndpointMixin


class PublicAdvocacyCampaignViewSet(PublicReadOnlyEndpointMixin):
    serializer_class = PublicAdvocacyCampaignSerializer
    permission_classes = [AllowAny]
    search_fields = ("title", "summary", "content", "slug")
    ordering_fields = ("title", "created_at", "updated_at")
    ordering = ("title",)

    def get_queryset(self):
        return get_public_advocacy_campaigns()


class AdminAdvocacyCampaignViewSet(AdminCrudEndpointMixin):
    serializer_class = AdvocacyCampaignSerializer
    permission_classes = [IsAdminPanelUser]
    filterset_fields = ("is_published",)
    search_fields = ("title", "summary", "content", "slug")
    ordering_fields = ("title", "created_at", "updated_at")
    ordering = ("title",)

    def get_queryset(self):
        return get_admin_advocacy_campaigns()
