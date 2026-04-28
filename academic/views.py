from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from accounts.permissions import IsAdminPanelUser
from academic.selectors import (
    get_admin_academic_digital_resource_configurations,
    get_admin_academic_services,
    get_admin_countdown_events,
    get_admin_quick_download_items,
    get_admin_youtube_sections,
    get_public_academic_services,
    get_public_countdown_events,
    get_public_quick_download_items,
    get_repository_materials,
)
from academic.serializers import (
    AcademicDigitalResourceConfigurationSerializer,
    AcademicDigitalResourcePayloadSerializer,
    AcademicServiceSerializer,
    CountdownEventSerializer,
    CountdownEventPublicSerializer,
    PublicAcademicServiceSerializer,
    QuickDownloadAdminSerializer,
    QuickDownloadPublicSerializer,
    RepositoryGroupedSerializer,
    RepositoryMaterialAdminSerializer,
    RepositoryMaterialPublicSerializer,
    YouTubeSectionAdminSerializer,
    YouTubeSectionPublicSerializer,
)
from academic.services import (
    build_repository_grouped_payload,
    get_active_academic_digital_resources_or_404,
    get_active_youtube_section_or_404,
)
from core.mixins import AdminCrudEndpointMixin, PublicReadOnlyEndpointMixin
from core.responses import success_response


class PublicAcademicServiceViewSet(PublicReadOnlyEndpointMixin):
    serializer_class = PublicAcademicServiceSerializer
    permission_classes = [AllowAny]
    search_fields = ("title", "description", "slug")
    ordering_fields = ("title", "published_at", "created_at")
    ordering = ("title",)

    def get_queryset(self):
        return get_public_academic_services()


class PublicQuickDownloadViewSet(PublicReadOnlyEndpointMixin):
    serializer_class = QuickDownloadPublicSerializer
    permission_classes = [AllowAny]
    search_fields = ("title",)
    ordering_fields = ("display_order", "title", "created_at")
    ordering = ("display_order", "title")

    def get_queryset(self):
        return get_public_quick_download_items()


class PublicRepositoryView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RepositoryGroupedSerializer

    def get(self, request):
        payload = build_repository_grouped_payload(RepositoryMaterialPublicSerializer)
        return success_response(payload, message="Repository materials retrieved successfully")


class PublicYouTubeSectionView(APIView):
    permission_classes = [AllowAny]
    serializer_class = YouTubeSectionPublicSerializer

    def get(self, request):
        section = get_active_youtube_section_or_404()
        serializer = YouTubeSectionPublicSerializer(section, context={"request": request})
        return success_response(serializer.data, message="Active YouTube section retrieved successfully")


class PublicCountdownEventViewSet(PublicReadOnlyEndpointMixin):
    serializer_class = CountdownEventPublicSerializer
    permission_classes = [AllowAny]
    search_fields = ("title",)
    ordering_fields = ("display_order", "target_datetime", "title")
    ordering = ("display_order", "target_datetime", "title")

    def get_queryset(self):
        return get_public_countdown_events()


class PublicAcademicDigitalResourcesView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AcademicDigitalResourcePayloadSerializer

    def get(self, request):
        configuration = get_active_academic_digital_resources_or_404()
        serializer = AcademicDigitalResourcePayloadSerializer(configuration, context={"request": request})
        return success_response(serializer.data, message="Academic digital resources retrieved successfully")


class AdminAcademicServiceViewSet(AdminCrudEndpointMixin):
    serializer_class = AcademicServiceSerializer
    permission_classes = [IsAdminPanelUser]
    filterset_fields = ("is_published",)
    search_fields = ("title", "description", "slug")
    ordering_fields = ("title", "published_at", "created_at", "updated_at")
    ordering = ("title",)

    def get_queryset(self):
        return get_admin_academic_services()


class AdminQuickDownloadViewSet(AdminCrudEndpointMixin):
    serializer_class = QuickDownloadAdminSerializer
    permission_classes = [IsAdminPanelUser]
    filterset_fields = ("is_active",)
    search_fields = ("title",)
    ordering_fields = ("display_order", "title", "created_at", "updated_at")
    ordering = ("display_order", "title")

    def get_queryset(self):
        return get_admin_quick_download_items()


class AdminRepositoryMaterialViewSet(AdminCrudEndpointMixin):
    serializer_class = RepositoryMaterialAdminSerializer
    permission_classes = [IsAdminPanelUser]
    filterset_fields = ("section",)
    search_fields = ("title", "google_drive_link")
    ordering_fields = ("section", "display_order", "title", "created_at")
    ordering = ("section", "display_order", "title")

    def get_queryset(self):
        return get_repository_materials()


class AdminYouTubeSectionViewSet(AdminCrudEndpointMixin):
    serializer_class = YouTubeSectionAdminSerializer
    permission_classes = [IsAdminPanelUser]
    filterset_fields = ("is_active",)
    search_fields = ("title", "description")
    ordering_fields = ("updated_at", "created_at", "title")
    ordering = ("-updated_at",)

    def get_queryset(self):
        return get_admin_youtube_sections()


class AdminCountdownEventViewSet(AdminCrudEndpointMixin):
    serializer_class = CountdownEventSerializer
    permission_classes = [IsAdminPanelUser]
    filterset_fields = ("is_active",)
    search_fields = ("title",)
    ordering_fields = ("display_order", "target_datetime", "created_at", "updated_at")
    ordering = ("display_order", "target_datetime", "title")

    def get_queryset(self):
        return get_admin_countdown_events()


class AdminAcademicDigitalResourceConfigurationViewSet(AdminCrudEndpointMixin):
    serializer_class = AcademicDigitalResourceConfigurationSerializer
    permission_classes = [IsAdminPanelUser]
    filterset_fields = ("is_active",)
    ordering_fields = ("updated_at", "created_at")
    ordering = ("-updated_at",)

    def get_queryset(self):
        return get_admin_academic_digital_resource_configurations()
