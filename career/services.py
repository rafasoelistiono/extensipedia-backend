from django.shortcuts import get_object_or_404

from career.models import CareerResourceConfiguration


def get_active_career_resources_or_404():
    return get_object_or_404(CareerResourceConfiguration, is_active=True)
