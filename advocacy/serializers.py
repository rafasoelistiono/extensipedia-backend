from rest_framework import serializers

from advocacy.models import AdvocacyCampaign
from core.serializers import BaseModelSerializer


class AdvocacyCampaignSerializer(BaseModelSerializer):
    class Meta:
        model = AdvocacyCampaign
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields


class PublicAdvocacyCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvocacyCampaign
        fields = ("id", "title", "slug", "summary", "content", "banner", "embed_url")
        read_only_fields = fields
