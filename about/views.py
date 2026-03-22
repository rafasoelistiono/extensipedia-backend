from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from accounts.permissions import IsAdminPanelUser
from about.selectors import (
    get_admin_cabinet_calendar,
    get_admin_hero_sections,
    get_admin_leadership_members,
    get_admin_organization_profiles,
    get_active_cabinet_calendar,
    get_public_leadership_members,
    get_public_organization_profiles,
)
from about.serializers import (
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
from about.services import (
    get_active_about_section_or_404,
    get_active_cabinet_calendar_or_404,
    get_active_hero_or_404,
    get_or_build_cabinet_calendar,
)
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


class PublicActiveCabinetCalendarView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PublicCabinetCalendarSerializer

    def get(self, request):
        calendar = get_active_cabinet_calendar_or_404()
        serializer = PublicCabinetCalendarSerializer(calendar, context={"request": request})
        return success_response(serializer.data, message="Active cabinet calendar retrieved successfully")


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


class AdminCabinetCalendarView(APIView):
    permission_classes = [IsAdminPanelUser]
    serializer_class = AdminCabinetCalendarSerializer

    def get_object(self):
        return get_admin_cabinet_calendar() or get_or_build_cabinet_calendar()

    def get(self, request):
        instance = self.get_object()
        serializer = AdminCabinetCalendarSerializer(instance, context={"request": request})
        return success_response(serializer.data, message="Cabinet calendar retrieved successfully")

    def put(self, request):
        return self._save(request, partial=False)

    def patch(self, request):
        return self._save(request, partial=True)

    def _save(self, request, partial):
        instance = get_admin_cabinet_calendar()
        serializer = AdminCabinetCalendarSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        save_kwargs = {"is_active": True, "updated_by": request.user}
        if instance is None:
            save_kwargs["created_by"] = request.user
        serializer.save(**save_kwargs)
        return success_response(serializer.data, message="Cabinet calendar updated successfully")
