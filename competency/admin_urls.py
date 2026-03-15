from rest_framework.routers import SimpleRouter

from competency.views import AdminAgendaCardViewSet, AdminCompetencyProgramViewSet

router = SimpleRouter()
router.register("programs", AdminCompetencyProgramViewSet, basename="admin-competency-programs")
router.register("agenda-cards", AdminAgendaCardViewSet, basename="admin-agenda-cards")

urlpatterns = router.urls
