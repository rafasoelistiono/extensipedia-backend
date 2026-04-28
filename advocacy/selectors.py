from advocacy.models import AdvocacyCampaign, AdvocacyPolicyResourceConfiguration


def get_public_advocacy_campaigns():
    return AdvocacyCampaign.objects.filter(is_published=True).select_related("created_by", "updated_by")


def get_admin_advocacy_campaigns():
    return AdvocacyCampaign.objects.select_related("created_by", "updated_by").all()


def get_admin_advocacy_policy_resource_configurations():
    return AdvocacyPolicyResourceConfiguration.objects.select_related("created_by", "updated_by").all()
