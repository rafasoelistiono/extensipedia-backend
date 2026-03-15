from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from accounts.permissions import IsAdminPanelUser
from analytics_dashboard.serializers import (
    DashboardSummarySerializer,
    PublicAnalyticsInfoSerializer,
    TicketLogItemSerializer,
)
from analytics_dashboard.services import build_dashboard_summary, build_recent_ticket_log
from core.responses import success_response


class PublicAnalyticsInfoView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PublicAnalyticsInfoSerializer

    def get(self, request):
        return success_response(
            {"available": False},
            message="Analytics dashboard is only available in the admin API",
        )


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
