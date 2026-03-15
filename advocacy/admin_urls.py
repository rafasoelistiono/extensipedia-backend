from rest_framework.routers import SimpleRouter

from advocacy.views import AdminAdvocacyCampaignViewSet

router = SimpleRouter()
router.register("campaigns", AdminAdvocacyCampaignViewSet, basename="admin-advocacy-campaigns")

urlpatterns = router.urls
