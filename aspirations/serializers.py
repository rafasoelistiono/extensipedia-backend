from rest_framework import serializers

from aspirations.models import AspirationSubmission
from core.serializers import BaseModelSerializer


class PublicAspirationSubmitSerializer(BaseModelSerializer):
    class Meta:
        model = AspirationSubmission
        fields = (
            "id",
            "full_name",
            "npm",
            "email",
            "title",
            "short_description",
            "evidence_attachment",
            "ticket_id",
            "status",
            "visibility",
            "is_featured",
            "upvote_count",
            "vote_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "ticket_id",
            "status",
            "visibility",
            "is_featured",
            "upvote_count",
            "vote_count",
            "created_at",
            "updated_at",
        )


class PublicFeaturedAspirationSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = AspirationSubmission
        fields = (
            "id",
            "ticket_id",
            "title",
            "short_description",
            "visibility",
            "sender_name",
            "status",
            "upvote_count",
            "vote_count",
            "created_at",
        )
        read_only_fields = fields

    def get_sender_name(self, obj) -> str | None:
        if obj.visibility == AspirationSubmission.Visibility.ANONYMOUS:
            return None
        return obj.full_name


class PublicTrackingSerializer(serializers.ModelSerializer):
    submitted_at = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = AspirationSubmission
        fields = (
            "ticket_id",
            "title",
            "status",
            "submitted_at",
            "updated_at",
            "visibility",
            "short_description",
        )
        read_only_fields = fields


class AdminAspirationListSerializer(BaseModelSerializer):
    class Meta:
        model = AspirationSubmission
        fields = (
            "id",
            "ticket_id",
            "full_name",
            "npm",
            "email",
            "title",
            "status",
            "visibility",
            "is_featured",
            "upvote_count",
            "vote_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class AdminAspirationDetailSerializer(BaseModelSerializer):
    class Meta:
        model = AspirationSubmission
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ("ticket_id", "upvote_count", "vote_count")

    def validate(self, attrs):
        is_featured = attrs.get("is_featured", getattr(self.instance, "is_featured", False))
        status = attrs.get("status", getattr(self.instance, "status", AspirationSubmission.Status.SUBMITTED))

        if is_featured and status == AspirationSubmission.Status.SUBMITTED:
            raise serializers.ValidationError(
                {"status": "Only investigating or resolved aspirations can be featured publicly."}
            )

        featured_queryset = AspirationSubmission.objects.filter(is_featured=True)
        if self.instance:
            featured_queryset = featured_queryset.exclude(pk=self.instance.pk)
        if is_featured and featured_queryset.count() >= AspirationSubmission.MAX_FEATURED:
            raise serializers.ValidationError(
                {"is_featured": f"Only {AspirationSubmission.MAX_FEATURED} aspirations can be featured at a time."}
            )
        return attrs


class SetFeaturedSerializer(serializers.Serializer):
    def validate(self, attrs):
        aspiration = self.context["aspiration"]
        featured_queryset = AspirationSubmission.objects.filter(is_featured=True).exclude(pk=aspiration.pk)
        if aspiration.status == AspirationSubmission.Status.SUBMITTED:
            raise serializers.ValidationError("Only investigating or resolved aspirations can be featured publicly.")
        if featured_queryset.count() >= AspirationSubmission.MAX_FEATURED:
            raise serializers.ValidationError(
                f"Only {AspirationSubmission.MAX_FEATURED} aspirations can be featured at a time."
            )
        return attrs
