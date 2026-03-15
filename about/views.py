from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from accounts.permissions import IsAdminPanelUser
from about.selectors import (
    get_admin_about_sections,
    get_admin_cabinet_calendars,
    get_admin_hero_sections,
    get_admin_leadership_members,
    get_admin_organization_profiles,
    get_public_cabinet_calendars,
    get_public_leadership_members,
    get_public_organization_profiles,
)
from about.serializers import (
    AboutSectionSerializer,
    AdminCabinetCalendarSerializer,
    HeroSectionSerializer,
    LeadershipMemberSerializer,
    OrganizationProfileSerializer,
    PublicAboutSectionSerializer,
    PublicCabinetCalendarSerializer,
    PublicHeroSectionSerializer,
    PublicLeadershipMemberSerializer,
    PublicOrganizationProfileSerializer,
)
from about.services import get_active_about_section_or_404, get_active_hero_or_404
from core.mixins import AdminCrudEndpointMixin, PublicReadOnlyEndpointMixin
from core.responses import success_response


class PublicOrganizationProfileViewSet(PublicReadOnlyEndpointMixin):
    serializer_class = PublicOrganizationProfileSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return get_public_organization_profiles()


class PublicLeadershipMemberViewSet(PublicReadOnlyEndpointMixin):
    serializer_class = PublicLeadershipMemberSerializer
    permission_classes = [AllowAny]
    search_fields = ("name", "role", "bio")
    ordering_fields = ("display_order", "name", "created_at")
    ordering = ("display_order", "name")

    def get_queryset(self):
        return get_public_leadership_members()


class PublicCabinetCalendarViewSet(PublicReadOnlyEndpointMixin):
    serializer_class = PublicCabinetCalendarSerializer
    permission_classes = [AllowAny]
    search_fields = ("title", "description", "provider")
    ordering_fields = ("display_order", "updated_at", "title")
    ordering = ("display_order", "-updated_at", "title")

    def get_queryset(self):
        return get_public_cabinet_calendars()


class PublicActiveHeroView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PublicHeroSectionSerializer

    def get(self, request):
        hero = get_active_hero_or_404()
        serializer = PublicHeroSectionSerializer(hero, context={"request": request})
        return success_response(serializer.data, message="Active hero section retrieved successfully")


class PublicActiveAboutSectionView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PublicAboutSectionSerializer

    def get(self, request):
        about_section = get_active_about_section_or_404()
        serializer = PublicAboutSectionSerializer(about_section, context={"request": request})
        return success_response(serializer.data, message="Active about section retrieved successfully")


class AdminOrganizationProfileViewSet(AdminCrudEndpointMixin):
    serializer_class = OrganizationProfileSerializer
    permission_classes = [IsAdminPanelUser]
    filterset_fields = ("is_active",)
    search_fields = ("name", "tagline", "summary", "contact_email")
    ordering_fields = ("name", "created_at", "updated_at")
    ordering = ("name",)

    def get_queryset(self):
        return get_admin_organization_profiles()


class AdminLeadershipMemberViewSet(AdminCrudEndpointMixin):
    serializer_class = LeadershipMemberSerializer
    permission_classes = [IsAdminPanelUser]
    filterset_fields = ("is_active",)
    search_fields = ("name", "role", "bio")
    ordering_fields = ("display_order", "name", "created_at", "updated_at")
    ordering = ("display_order", "name")

    def get_queryset(self):
        return get_admin_leadership_members()


class AdminHeroSectionViewSet(AdminCrudEndpointMixin):
    serializer_class = HeroSectionSerializer
    permission_classes = [IsAdminPanelUser]
    filterset_fields = ("is_active",)
    search_fields = ("title", "subtitle", "description")
    ordering_fields = ("updated_at", "created_at", "title")
    ordering = ("-updated_at",)

    def get_queryset(self):
        return get_admin_hero_sections()


class AdminAboutSectionViewSet(AdminCrudEndpointMixin):
    serializer_class = AboutSectionSerializer
    permission_classes = [IsAdminPanelUser]
    filterset_fields = ("is_active",)
    search_fields = ("title", "subtitle", "description")
    ordering_fields = ("updated_at", "created_at", "title")
    ordering = ("-updated_at",)

    def get_queryset(self):
        return get_admin_about_sections()


class AdminCabinetCalendarViewSet(AdminCrudEndpointMixin):
    serializer_class = AdminCabinetCalendarSerializer
    permission_classes = [IsAdminPanelUser]
    filterset_fields = ("is_active", "provider")
    search_fields = ("title", "description", "provider")
    ordering_fields = ("display_order", "updated_at", "title")
    ordering = ("display_order", "-updated_at", "title")

    def get_queryset(self):
        return get_admin_cabinet_calendars()
