from django.urls import path

from aspirations.views import (
    PublicAspirationSubmitView,
    PublicAspirationUpvoteView,
    PublicAspirationVoteView,
    PublicFeaturedAspirationView,
)

urlpatterns = [
    path("submit/", PublicAspirationSubmitView.as_view(), name="aspiration-submit"),
    path("featured/", PublicFeaturedAspirationView.as_view(), name="aspiration-featured"),
    path("<uuid:pk>/upvote/", PublicAspirationUpvoteView.as_view(), name="aspiration-upvote"),
    path("<uuid:pk>/vote/", PublicAspirationVoteView.as_view(), name="aspiration-vote"),
]
