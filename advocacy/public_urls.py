from django.urls import path
from rest_framework.routers import SimpleRouter

from advocacy.views import PublicAdvocacyCampaignViewSet, PublicAdvocacyPolicyResourcesView

router = SimpleRouter()
router.register("campaigns", PublicAdvocacyCampaignViewSet, basename="public-advocacy-campaigns")

urlpatterns = [
    path("policy-resources/", PublicAdvocacyPolicyResourcesView.as_view(), name="public-policy-resources"),
]
urlpatterns += router.urls
