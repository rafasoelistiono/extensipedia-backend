from rest_framework import serializers

from academic.models import (
    AcademicDigitalResourceConfiguration,
    AcademicService,
    CountdownEvent,
    QuickDownloadItem,
    RepositoryMaterial,
    YouTubeSection,
)
from core.serializers import BaseModelSerializer
from core.validators import validate_google_drive_url, validate_iframe_or_embed_input


class AcademicServiceSerializer(BaseModelSerializer):
    class Meta:
        model = AcademicService
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields


class PublicAcademicServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicService
        fields = ("id", "title", "slug", "description", "thumbnail", "published_at")
        read_only_fields = fields


class QuickDownloadAdminSerializer(BaseModelSerializer):
    class Meta:
        model = QuickDownloadItem
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields

    def validate(self, attrs):
        file = attrs.get("file")
        external_url = attrs.get("external_url")

        if self.instance is not None:
            file = file if file is not None else self.instance.file
            external_url = external_url if external_url is not None else self.instance.external_url

        if bool(file) == bool(external_url):
            raise serializers.ValidationError("Provide either a file upload or an external URL.")

        queryset = QuickDownloadItem.objects.all()
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.count() >= QuickDownloadItem.MAX_ITEMS:
            raise serializers.ValidationError(
                f"Quick downloads support a maximum of {QuickDownloadItem.MAX_ITEMS} items."
            )
        return attrs


class QuickDownloadPublicSerializer(serializers.ModelSerializer):
    resource_type = serializers.SerializerMethodField()
    resource_url = serializers.SerializerMethodField()

    class Meta:
        model = QuickDownloadItem
        fields = ("id", "title", "resource_type", "resource_url", "display_order")
        read_only_fields = fields

    def get_resource_type(self, obj) -> str:
        return "file" if obj.file else "external_link"

    def get_resource_url(self, obj) -> str:
        request = self.context.get("request")
        if obj.file:
            url = obj.file.url
            return request.build_absolute_uri(url) if request else url
        return obj.external_url


class RepositoryMaterialAdminSerializer(BaseModelSerializer):
    class Meta:
        model = RepositoryMaterial
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields

    def validate(self, attrs):
        section = attrs.get("section") or getattr(self.instance, "section", None)
        google_drive_link = attrs.get("google_drive_link") or getattr(self.instance, "google_drive_link", None)

        if google_drive_link:
            validate_google_drive_url(google_drive_link)

        queryset = RepositoryMaterial.objects.filter(section=section)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.count() >= RepositoryMaterial.MAX_ITEMS_PER_SECTION:
            raise serializers.ValidationError(
                f"Section {dict(RepositoryMaterial.Sections.choices)[section]} supports a maximum of "
                f"{RepositoryMaterial.MAX_ITEMS_PER_SECTION} items."
            )
        return attrs


class RepositoryMaterialPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryMaterial
        fields = ("id", "title", "google_drive_link", "display_order")
        read_only_fields = fields


class RepositoryGroupedSerializer(serializers.Serializer):
    akuntansi = RepositoryMaterialPublicSerializer(many=True)
    manajemen = RepositoryMaterialPublicSerializer(many=True)


class YouTubeSectionAdminSerializer(BaseModelSerializer):
    class Meta:
        model = YouTubeSection
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ("sanitized_embed_url",)

    def validate(self, attrs):
        embed_url = attrs.get("embed_url")
        embed_code = attrs.get("embed_code")

        if self.instance is not None:
            embed_url = embed_url if embed_url is not None else self.instance.embed_url
            embed_code = embed_code if embed_code is not None else self.instance.embed_code

        validate_iframe_or_embed_input(embed_url, embed_code)
        return attrs


class YouTubeSectionPublicSerializer(serializers.ModelSerializer):
    embed_url = serializers.URLField(source="sanitized_embed_url", read_only=True)

    class Meta:
        model = YouTubeSection
        fields = ("id", "title", "description", "embed_url")
        read_only_fields = fields


class CountdownEventSerializer(BaseModelSerializer):
    class Meta:
        model = CountdownEvent
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields


class CountdownEventPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountdownEvent
        fields = ("id", "title", "target_datetime", "display_order")
        read_only_fields = fields


class AcademicDigitalResourceConfigurationSerializer(BaseModelSerializer):
    class Meta:
        model = AcademicDigitalResourceConfiguration
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields


class AcademicDigitalResourcePayloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicDigitalResourceConfiguration
        fields = ("id", "canva_pro_ekstensi", "gemini_advanced")
        read_only_fields = fields
