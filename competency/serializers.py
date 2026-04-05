from django.utils import timezone
from rest_framework import serializers

from competency.models import AgendaCard, CompetencyProgram, CompetencyWinnerSlide
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


class CompetencyWinnerSlideAdminSerializer(BaseModelSerializer):
    class Meta:
        model = CompetencyWinnerSlide
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields

    def validate(self, attrs):
        publish_start_at = attrs.get("publish_start_at", getattr(self.instance, "publish_start_at", None))
        publish_end_at = attrs.get("publish_end_at", getattr(self.instance, "publish_end_at", None))
        queryset = CompetencyWinnerSlide.objects.all()
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.count() >= CompetencyWinnerSlide.MAX_RECORDS and self.instance is None:
            raise serializers.ValidationError(
                f"Winner slides support a maximum of {CompetencyWinnerSlide.MAX_RECORDS} records."
            )
        if publish_start_at and publish_end_at and publish_end_at < publish_start_at:
            raise serializers.ValidationError(
                {"publish_end_at": "Publish end time must be greater than or equal to publish start time."}
            )
        return attrs


class CompetencyWinnerSlidePublicSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    mobile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = CompetencyWinnerSlide
        fields = (
            "id",
            "title",
            "image_url",
            "mobile_image_url",
            "alt_text",
            "caption",
            "cta_label",
            "cta_url",
            "display_order",
            "publish_start_at",
            "publish_end_at",
            "updated_at",
        )
        read_only_fields = fields

    def build_absolute_url(self, file_field):
        if not file_field:
            return None
        request = self.context.get("request")
        url = file_field.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url

    def get_image_url(self, obj):
        return self.build_absolute_url(obj.image)

    def get_mobile_image_url(self, obj):
        return self.build_absolute_url(obj.mobile_image)


class WinnerSlideReorderItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    display_order = serializers.IntegerField(min_value=1, max_value=CompetencyWinnerSlide.MAX_RECORDS)


class WinnerSlideReorderSerializer(serializers.Serializer):
    items = WinnerSlideReorderItemSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Provide at least one winner slide item.")
        return value
