from rest_framework.routers import SimpleRouter

from aspirations.views import AdminAspirationSubmissionViewSet

router = SimpleRouter()
router.register("submissions", AdminAspirationSubmissionViewSet, basename="admin-aspiration-submissions")

urlpatterns = router.urls
