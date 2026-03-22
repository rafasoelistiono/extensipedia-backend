from django.urls import path

from about.views import (
    AdminCabinetCalendarView,
    AdminHeroSectionViewSet,
    AdminLeadershipMemberViewSet,
    AdminOrganizationProfileViewSet,
)

from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register("profiles", AdminOrganizationProfileViewSet, basename="admin-profiles")
router.register("leadership", AdminLeadershipMemberViewSet, basename="admin-leadership")
router.register("heroes", AdminHeroSectionViewSet, basename="admin-heroes")

urlpatterns = [
    path("cabinet-calendar/", AdminCabinetCalendarView.as_view(), name="admin-cabinet-calendar"),
]
urlpatterns += router.urls
