from rest_framework.routers import SimpleRouter

from advocacy.views import PublicAdvocacyCampaignViewSet

router = SimpleRouter()
router.register("campaigns", PublicAdvocacyCampaignViewSet, basename="public-advocacy-campaigns")

urlpatterns = router.urls
