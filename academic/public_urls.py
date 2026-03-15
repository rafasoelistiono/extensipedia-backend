from django.urls import path
from rest_framework.routers import SimpleRouter

from academic.views import (
    PublicAcademicServiceViewSet,
    PublicCountdownEventViewSet,
    PublicQuickDownloadViewSet,
    PublicRepositoryView,
    PublicYouTubeSectionView,
)

router = SimpleRouter()
router.register("services", PublicAcademicServiceViewSet, basename="public-academic-services")
router.register("quick-downloads", PublicQuickDownloadViewSet, basename="public-quick-downloads")
router.register("countdown-events", PublicCountdownEventViewSet, basename="public-countdown-events")

urlpatterns = [
    path("repository/", PublicRepositoryView.as_view(), name="public-repository"),
    path("youtube/", PublicYouTubeSectionView.as_view(), name="public-youtube"),
]
urlpatterns += router.urls
