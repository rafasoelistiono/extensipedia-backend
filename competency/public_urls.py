from rest_framework.routers import SimpleRouter

from competency.views import PublicAgendaCardViewSet, PublicCompetencyProgramViewSet, PublicCompetencyWinnerSlideViewSet

router = SimpleRouter()
router.register("programs", PublicCompetencyProgramViewSet, basename="public-competency-programs")
router.register("agenda-cards", PublicAgendaCardViewSet, basename="public-agenda-cards")
router.register("winner-slides", PublicCompetencyWinnerSlideViewSet, basename="public-competency-winner-slides")

urlpatterns = router.urls
