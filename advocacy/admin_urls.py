from rest_framework.routers import SimpleRouter

from advocacy.views import AdminAdvocacyCampaignViewSet, AdminAdvocacyPolicyResourceConfigurationViewSet

router = SimpleRouter()
router.register("campaigns", AdminAdvocacyCampaignViewSet, basename="admin-advocacy-campaigns")
router.register(
    "policy-resources",
    AdminAdvocacyPolicyResourceConfigurationViewSet,
    basename="admin-policy-resources",
)

urlpatterns = router.urls
