from rest_framework.permissions import AllowAny

from accounts.permissions import IsAdminPanelUser
from competency.selectors import (
    get_admin_agenda_cards,
    get_admin_competency_programs,
    get_admin_winner_slides,
    get_public_agenda_cards,
    get_public_competency_programs,
    get_public_winner_slides,
)
from competency.serializers import (
    AgendaCardAdminSerializer,
    AgendaCardPublicSerializer,
    CompetencyProgramSerializer,
    CompetencyWinnerSlideAdminSerializer,
    CompetencyWinnerSlidePublicSerializer,
    PublicCompetencyProgramSerializer,
)
from core.mixins import AdminCrudEndpointMixin, PublicReadOnlyEndpointMixin


class PublicCompetencyProgramViewSet(PublicReadOnlyEndpointMixin):
    serializer_class = PublicCompetencyProgramSerializer
    permission_classes = [AllowAny]
    search_fields = ("title", "description", "slug")
    ordering_fields = ("title", "starts_at", "ends_at", "created_at")
    ordering = ("title",)

    def get_queryset(self):
        return get_public_competency_programs()


class PublicAgendaCardViewSet(PublicReadOnlyEndpointMixin):
    serializer_class = AgendaCardPublicSerializer
    permission_classes = [AllowAny]
    search_fields = ("title", "short_description", "category_tag", "scope_tag", "pricing_tag")
    ordering_fields = ("created_at", "updated_at", "deadline_date", "title")
    ordering = ("-created_at", "-updated_at", "deadline_date", "title")

    def get_queryset(self):
        return get_public_agenda_cards(self.request.query_params)


class AdminCompetencyProgramViewSet(AdminCrudEndpointMixin):
    serializer_class = CompetencyProgramSerializer
    permission_classes = [IsAdminPanelUser]
    filterset_fields = ("is_published",)
    search_fields = ("title", "description", "slug")
    ordering_fields = ("title", "starts_at", "ends_at", "created_at", "updated_at")
    ordering = ("title",)

    def get_queryset(self):
        return get_admin_competency_programs()


class AdminAgendaCardViewSet(AdminCrudEndpointMixin):
    serializer_class = AgendaCardAdminSerializer
    permission_classes = [IsAdminPanelUser]
    filterset_fields = ("is_active", "urgency_tag", "recommendation_tag", "category_tag", "scope_tag", "pricing_tag")
    search_fields = ("title", "short_description", "category_tag", "scope_tag", "pricing_tag")
    ordering_fields = ("deadline_date", "created_at", "updated_at", "title")
    ordering = ("-created_at", "-updated_at", "deadline_date", "title")

    def get_queryset(self):
        return get_admin_agenda_cards()


class PublicCompetencyWinnerSlideViewSet(PublicReadOnlyEndpointMixin):
    serializer_class = CompetencyWinnerSlidePublicSerializer
    permission_classes = [AllowAny]
    ordering_fields = ("display_order", "updated_at", "created_at")
    ordering = ("display_order", "-updated_at")

    def get_queryset(self):
        return get_public_winner_slides()


class AdminCompetencyWinnerSlideViewSet(AdminCrudEndpointMixin):
    serializer_class = CompetencyWinnerSlideAdminSerializer
    permission_classes = [IsAdminPanelUser]
    http_method_names = ["get", "patch", "head", "options"]
    filterset_fields = ("display_order",)
    search_fields = ("alt_text",)
    ordering_fields = ("display_order", "created_at", "updated_at")
    ordering = ("display_order", "-updated_at")

    def get_queryset(self):
        return get_admin_winner_slides()
