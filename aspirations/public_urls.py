from django.urls import path

from aspirations.views import (
    PublicAspirationSubmitView,
    PublicAspirationUpvoteView,
    PublicAspirationVoteView,
    PublicFeaturedAspirationView,
)

urlpatterns = [
    path("submit/", PublicAspirationSubmitView.as_view(), name="aspiration-submit"),
    path("submit", PublicAspirationSubmitView.as_view()),
    path("featured/", PublicFeaturedAspirationView.as_view(), name="aspiration-featured"),
    path("<uuid:pk>/upvote/", PublicAspirationUpvoteView.as_view(), name="aspiration-upvote"),
    path("<uuid:pk>/upvote", PublicAspirationUpvoteView.as_view()),
    path("<uuid:pk>/vote/", PublicAspirationVoteView.as_view(), name="aspiration-vote"),
    path("<uuid:pk>/vote", PublicAspirationVoteView.as_view()),
]
