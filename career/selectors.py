from career.models import CareerOpportunity, CareerResourceConfiguration


def get_public_career_opportunities():
    return CareerOpportunity.objects.filter(is_published=True).select_related("created_by", "updated_by")


def get_admin_career_opportunities():
    return CareerOpportunity.objects.select_related("created_by", "updated_by").all()


def get_admin_career_resource_configurations():
    return CareerResourceConfiguration.objects.select_related("created_by", "updated_by").all()


def get_active_career_resource_configuration():
    return CareerResourceConfiguration.objects.filter(is_active=True).select_related("created_by", "updated_by").first()
