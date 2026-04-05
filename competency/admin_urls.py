from rest_framework.routers import SimpleRouter

from competency.views import AdminAgendaCardViewSet, AdminCompetencyProgramViewSet, AdminCompetencyWinnerSlideViewSet

router = SimpleRouter()
router.register("programs", AdminCompetencyProgramViewSet, basename="admin-competency-programs")
router.register("agenda-cards", AdminAgendaCardViewSet, basename="admin-agenda-cards")
router.register("winner-slides", AdminCompetencyWinnerSlideViewSet, basename="admin-competency-winner-slides")

urlpatterns = router.urls
