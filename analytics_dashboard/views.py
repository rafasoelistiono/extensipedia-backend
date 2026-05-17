from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from accounts.permissions import IsAdminPanelUser
from analytics_dashboard.serializers import (
    DashboardSummarySerializer,
    PublicActivityEventResultSerializer,
    PublicActivityEventSerializer,
    PublicAnalyticsInfoSerializer,
    TicketLogItemSerializer,
)
from analytics_dashboard.services import build_dashboard_summary, build_recent_ticket_log, record_public_activity_event
from analytics_dashboard.throttles import PublicActivityEventThrottle
from core.responses import success_response


class PublicAnalyticsInfoView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PublicAnalyticsInfoSerializer

    def get(self, request):
        return success_response(
            {"available": False},
            message="Analytics dashboard is only available in the admin API",
        )


class PublicActivityEventView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PublicActivityEventThrottle]
    serializer_class = PublicActivityEventSerializer

    def post(self, request):
        serializer = PublicActivityEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = record_public_activity_event(serializer.validated_data, request)
        result_serializer = PublicActivityEventResultSerializer(payload)
        return success_response(result_serializer.data, message="Activity recorded")


class DashboardSummaryView(APIView):
    permission_classes = [IsAdminPanelUser]
    serializer_class = DashboardSummarySerializer

    def get(self, request):
        payload = build_dashboard_summary()
        serializer = DashboardSummarySerializer(payload)
        return success_response(serializer.data, message="Dashboard summary retrieved successfully")


class TicketLogView(APIView):
    permission_classes = [IsAdminPanelUser]
    serializer_class = TicketLogItemSerializer

    def get(self, request):
        logs = build_recent_ticket_log(limit=20)
        serializer = TicketLogItemSerializer(logs, many=True)
        return success_response(serializer.data, message="Ticket activity log retrieved successfully")
