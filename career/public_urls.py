from django.urls import path
from rest_framework.routers import SimpleRouter

from career.views import PublicCareerOpportunityViewSet, PublicCareerResourcesView

router = SimpleRouter()
router.register("opportunities", PublicCareerOpportunityViewSet, basename="public-career-opportunities")

urlpatterns = [
    path("resources/", PublicCareerResourcesView.as_view(), name="public-career-resources"),
]
urlpatterns += router.urls
