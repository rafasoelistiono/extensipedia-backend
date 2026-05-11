from rest_framework import serializers

from about.models import (
    ABOUT_PROGRAM_LINK_GROUPS,
    AboutSection,
    CabinetCalendar,
    HeroSection,
    LeadershipMember,
    OrganizationProfile,
)
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
    program_detail_links = serializers.SerializerMethodField()

    class Meta:
        model = AboutSection
        fields = (
            "id",
            "title",
            "subtitle",
            "description",
            "image",
            "extensipedia_link",
            "study_boost_exam_blast_link",
            "fun_enlightenment_link",
            "career_catalyst_link",
            "explore_link",
            "business_partnership_link",
            "jaring_aspirasi_link",
            "kajian_strategis_link",
            "bincang_sekma_link",
            "reach_project_link",
            "talent_interest_link",
            "branding_dokumentasi_link",
            "program_detail_links",
        )
        read_only_fields = fields

    def get_program_detail_links(self, obj):
        return [
            {
                "key": group_key,
                "label": group_label,
                "links": [
                    {
                        "key": field_name,
                        "label": item_label,
                        "url": getattr(obj, field_name, ""),
                    }
                    for field_name, item_label in items
                ],
            }
            for group_key, group_label, items in ABOUT_PROGRAM_LINK_GROUPS
        ]


class AdminCabinetCalendarSerializer(BaseModelSerializer):
    class Meta:
        model = CabinetCalendar
        fields = (
            "id",
            "title",
            "description",
            "embed_url",
            "embed_code",
            "sanitized_embed_url",
            "provider",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )
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
            "embed_code",
            "provider",
        )
        read_only_fields = fields
