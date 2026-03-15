from rest_framework import serializers

from aspirations.models import AspirationActivityLog


class DashboardStatusCountSerializer(serializers.Serializer):
    submitted = serializers.IntegerField()
    investigating = serializers.IntegerField()
    resolved = serializers.IntegerField()


class DashboardCardsSerializer(serializers.Serializer):
    total_aspiration_submissions = serializers.IntegerField()
    status_counts = DashboardStatusCountSerializer()
    total_featured_aspirations = serializers.IntegerField()
    total_visitors_last_30_days = serializers.IntegerField()


class DailyVisitorPointSerializer(serializers.Serializer):
    date = serializers.DateField()
    count = serializers.IntegerField()


class DashboardChartsSerializer(serializers.Serializer):
    daily_visitors_last_30_days = DailyVisitorPointSerializer(many=True)


class DashboardSummarySerializer(serializers.Serializer):
    cards = DashboardCardsSerializer()
    charts = DashboardChartsSerializer()


class TicketLogItemSerializer(serializers.ModelSerializer):
    ticket_id = serializers.CharField(source="aspiration.ticket_id", read_only=True)
    title = serializers.CharField(source="aspiration.title", read_only=True)

    class Meta:
        model = AspirationActivityLog
        fields = (
            "id",
            "ticket_id",
            "title",
            "action",
            "message",
            "actor_name",
            "status_snapshot",
            "visibility_snapshot",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class PublicAnalyticsInfoSerializer(serializers.Serializer):
    available = serializers.BooleanField()
