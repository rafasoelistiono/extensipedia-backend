from rest_framework.routers import SimpleRouter

from career.views import AdminCareerOpportunityViewSet, AdminCareerResourceConfigurationViewSet

router = SimpleRouter()
router.register("opportunities", AdminCareerOpportunityViewSet, basename="admin-career-opportunities")
router.register("resources", AdminCareerResourceConfigurationViewSet, basename="admin-career-resources")

urlpatterns = router.urls
