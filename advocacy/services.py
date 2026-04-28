from django.shortcuts import get_object_or_404

from advocacy.models import AdvocacyPolicyResourceConfiguration


def get_active_advocacy_policy_resources_or_404():
    return get_object_or_404(AdvocacyPolicyResourceConfiguration, is_active=True)
