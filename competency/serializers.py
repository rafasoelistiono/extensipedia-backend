from django.utils import timezone
from rest_framework import serializers

from competency.models import AgendaCard, CompetencyProgram
from core.serializers import BaseModelSerializer


class CompetencyProgramSerializer(BaseModelSerializer):
    class Meta:
        model = CompetencyProgram
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields


class PublicCompetencyProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetencyProgram
        fields = ("id", "title", "slug", "description", "poster", "starts_at", "ends_at")
        read_only_fields = fields


class AgendaCardAdminSerializer(BaseModelSerializer):
    class Meta:
        model = AgendaCard
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields

    def validate(self, attrs):
        queryset = AgendaCard.objects.all()
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.count() >= AgendaCard.MAX_RECORDS:
            raise serializers.ValidationError(
                f"Competency agenda cards support a maximum of {AgendaCard.MAX_RECORDS} records."
            )
        return attrs


class AgendaCardPublicSerializer(serializers.ModelSerializer):
    countdown_days = serializers.SerializerMethodField()

    class Meta:
        model = AgendaCard
        fields = (
            "id",
            "title",
            "short_description",
            "urgency_tag",
            "recommendation_tag",
            "category_tag",
            "scope_tag",
            "pricing_tag",
            "deadline_date",
            "registration_link",
            "google_calendar_link",
            "countdown_days",
        )
        read_only_fields = fields

    def get_countdown_days(self, obj) -> int:
        return (obj.deadline_date - timezone.localdate()).days
