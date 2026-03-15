from rest_framework import serializers

from career.models import CareerOpportunity, CareerResourceConfiguration
from core.serializers import BaseModelSerializer


class CareerOpportunitySerializer(BaseModelSerializer):
    class Meta:
        model = CareerOpportunity
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields


class CareerResourceConfigurationSerializer(BaseModelSerializer):
    class Meta:
        model = CareerResourceConfiguration
        fields = "__all__"
        read_only_fields = BaseModelSerializer.Meta.read_only_fields


class PublicCareerOpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerOpportunity
        fields = ("id", "title", "organization", "description", "apply_url", "closes_at")
        read_only_fields = fields


class CareerResourcePayloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerResourceConfiguration
        fields = (
            "id",
            "cv_templates",
            "cover_letter",
            "portfolio_guide",
            "salary_script",
            "case_study_interview_prep",
        )
        read_only_fields = fields
