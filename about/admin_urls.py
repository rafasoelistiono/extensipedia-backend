from rest_framework.routers import SimpleRouter

from about.views import (
    AdminAboutSectionViewSet,
    AdminCabinetCalendarViewSet,
    AdminHeroSectionViewSet,
    AdminLeadershipMemberViewSet,
    AdminOrganizationProfileViewSet,
)

router = SimpleRouter()
router.register("profiles", AdminOrganizationProfileViewSet, basename="admin-profiles")
router.register("leadership", AdminLeadershipMemberViewSet, basename="admin-leadership")
router.register("heroes", AdminHeroSectionViewSet, basename="admin-heroes")
router.register("tentang-kami", AdminAboutSectionViewSet, basename="admin-tentang-kami")
router.register("cabinet-calendars", AdminCabinetCalendarViewSet, basename="admin-cabinet-calendars")

urlpatterns = router.urls
