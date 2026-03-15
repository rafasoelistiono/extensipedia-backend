from rest_framework.routers import SimpleRouter

from competency.views import PublicAgendaCardViewSet, PublicCompetencyProgramViewSet

router = SimpleRouter()
router.register("programs", PublicCompetencyProgramViewSet, basename="public-competency-programs")
router.register("agenda-cards", PublicAgendaCardViewSet, basename="public-agenda-cards")

urlpatterns = router.urls
