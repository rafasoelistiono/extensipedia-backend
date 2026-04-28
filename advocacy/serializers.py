from rest_framework import serializers

from advocacy.models import AdvocacyCampaign, AdvocacyPolicyResourceConfiguration
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


class AdvocacyPolicyResourceConfigurationSerializer(BaseModelSerializer):
    class Meta:
        model = AdvocacyPolicyResourceConfiguration
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields


class AdvocacyPolicyResourcePayloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvocacyPolicyResourceConfiguration
        fields = ("id", "siak_war", "cicilan_ukt", "alur_skpi")
        read_only_fields = fields
