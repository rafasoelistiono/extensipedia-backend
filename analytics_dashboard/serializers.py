from rest_framework import serializers

from aspirations.models import AspirationActivityLog
from analytics_dashboard.models import ActivityActionKey


class DashboardStatusCountSerializer(serializers.Serializer):
    submitted = serializers.IntegerField()
    investigating = serializers.IntegerField()
    resolved = serializers.IntegerField()


class DashboardCardsSerializer(serializers.Serializer):
    total_aspiration_submissions = serializers.IntegerField()
    status_counts = DashboardStatusCountSerializer()
    total_featured_aspirations = serializers.IntegerField()
    total_activity_events_all_time = serializers.IntegerField()


class DashboardChartsSerializer(serializers.Serializer):
    pass


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


class PublicActivityEventSerializer(serializers.Serializer):
    action_key = serializers.ChoiceField(choices=ActivityActionKey.choices)
    label = serializers.CharField(max_length=120)
    page_path = serializers.CharField(max_length=255)
    target_type = serializers.CharField(max_length=64)
    target_id = serializers.CharField(max_length=64, allow_null=True, allow_blank=True, required=False)
    target_url = serializers.CharField(max_length=1000, allow_null=True, allow_blank=True, required=False)
    metadata = serializers.JSONField(required=False, default=dict)
    idempotency_key = serializers.CharField(max_length=120, allow_blank=True, required=False)

    def validate_metadata(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Metadata must be an object.")
        return value

    def validate_idempotency_key(self, value):
        return value.strip() or None


class PublicActivityEventResultSerializer(serializers.Serializer):
    action_key = serializers.ChoiceField(choices=ActivityActionKey.choices)
    total_count = serializers.IntegerField()
