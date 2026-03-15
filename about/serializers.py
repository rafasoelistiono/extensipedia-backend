from rest_framework import serializers

from about.models import AboutSection, CabinetCalendar, HeroSection, LeadershipMember, OrganizationProfile
from core.serializers import BaseModelSerializer
from core.validators import validate_iframe_or_embed_input


class OrganizationProfileSerializer(BaseModelSerializer):
    class Meta:
        model = OrganizationProfile
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields


class LeadershipMemberSerializer(BaseModelSerializer):
    class Meta:
        model = LeadershipMember
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields


class HeroSectionSerializer(BaseModelSerializer):
    class Meta:
        model = HeroSection
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields


class AboutSectionSerializer(BaseModelSerializer):
    class Meta:
        model = AboutSection
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields


class PublicOrganizationProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationProfile
        fields = (
            "id",
            "name",
            "tagline",
            "summary",
            "vision",
            "mission",
            "logo",
            "contact_email",
            "contact_phone",
            "address",
        )
        read_only_fields = fields


class PublicLeadershipMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadershipMember
        fields = ("id", "name", "role", "bio", "photo", "display_order")
        read_only_fields = fields


class PublicHeroSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroSection
        fields = (
            "id",
            "title",
            "subtitle",
            "description",
            "image",
            "primary_button_label",
            "primary_button_url",
            "secondary_button_label",
            "secondary_button_url",
        )
        read_only_fields = fields


class PublicAboutSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutSection
        fields = ("id", "title", "subtitle", "description", "image")
        read_only_fields = fields


class AdminCabinetCalendarSerializer(BaseModelSerializer):
    class Meta:
        model = CabinetCalendar
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ("sanitized_embed_url", "provider")

    def validate(self, attrs):
        embed_url = attrs.get("embed_url")
        embed_code = attrs.get("embed_code")

        if self.instance is not None:
            embed_url = embed_url if embed_url is not None else self.instance.embed_url
            embed_code = embed_code if embed_code is not None else self.instance.embed_code

        validate_iframe_or_embed_input(embed_url, embed_code)
        return attrs


class PublicCabinetCalendarSerializer(serializers.ModelSerializer):
    embed_url = serializers.URLField(source="sanitized_embed_url", read_only=True)

    class Meta:
        model = CabinetCalendar
        fields = (
            "id",
            "title",
            "description",
            "embed_url",
            "provider",
            "display_order",
        )
        read_only_fields = fields
