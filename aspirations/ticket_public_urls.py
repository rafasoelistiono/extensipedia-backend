from django.urls import path

from aspirations.views import PublicTicketTrackingView

urlpatterns = [
    path("track/", PublicTicketTrackingView.as_view(), name="ticket-track"),
]
