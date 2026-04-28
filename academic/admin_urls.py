from rest_framework.routers import SimpleRouter

from academic.views import (
    AdminAcademicDigitalResourceConfigurationViewSet,
    AdminAcademicServiceViewSet,
    AdminCountdownEventViewSet,
    AdminQuickDownloadViewSet,
    AdminRepositoryMaterialViewSet,
    AdminYouTubeSectionViewSet,
)

router = SimpleRouter()
router.register("services", AdminAcademicServiceViewSet, basename="admin-academic-services")
router.register("quick-downloads", AdminQuickDownloadViewSet, basename="admin-quick-downloads")
router.register("repository-materials", AdminRepositoryMaterialViewSet, basename="admin-repository-materials")
router.register("youtube-sections", AdminYouTubeSectionViewSet, basename="admin-youtube-sections")
router.register("countdown-events", AdminCountdownEventViewSet, basename="admin-countdown-events")
router.register(
    "digital-resources",
    AdminAcademicDigitalResourceConfigurationViewSet,
    basename="admin-digital-resources",
)

urlpatterns = router.urls
