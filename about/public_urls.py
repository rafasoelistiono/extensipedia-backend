from django.urls import path
from rest_framework.routers import SimpleRouter

from about.views import (
    PublicActiveAboutSectionView,
    PublicActiveCabinetCalendarView,
    PublicActiveHeroView,
    PublicLeadershipMemberViewSet,
    PublicOrganizationProfileViewSet,
)

router = SimpleRouter()
router.register("profiles", PublicOrganizationProfileViewSet, basename="public-profiles")
router.register("leadership", PublicLeadershipMemberViewSet, basename="public-leadership")

urlpatterns = [
    path("hero/", PublicActiveHeroView.as_view(), name="public-hero"),
    path("tentang-kami/", PublicActiveAboutSectionView.as_view(), name="public-tentang-kami"),
    path("cabinet-calendar/", PublicActiveCabinetCalendarView.as_view(), name="public-cabinet-calendar"),
]
urlpatterns += router.urls
