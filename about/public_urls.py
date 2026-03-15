from django.urls import path
from rest_framework.routers import SimpleRouter

from about.views import (
    PublicActiveAboutSectionView,
    PublicActiveHeroView,
    PublicCabinetCalendarViewSet,
    PublicLeadershipMemberViewSet,
    PublicOrganizationProfileViewSet,
)

router = SimpleRouter()
router.register("profiles", PublicOrganizationProfileViewSet, basename="public-profiles")
router.register("leadership", PublicLeadershipMemberViewSet, basename="public-leadership")
router.register("cabinet-calendars", PublicCabinetCalendarViewSet, basename="public-cabinet-calendars")

urlpatterns = [
    path("hero/", PublicActiveHeroView.as_view(), name="public-hero"),
    path("tentang-kami/", PublicActiveAboutSectionView.as_view(), name="public-tentang-kami"),
]
urlpatterns += router.urls
