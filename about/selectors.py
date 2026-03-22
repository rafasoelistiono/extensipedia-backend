from about.models import AboutSection, CabinetCalendar, HeroSection, LeadershipMember, OrganizationProfile


def get_public_organization_profiles():
    return OrganizationProfile.objects.filter(is_active=True).select_related("created_by", "updated_by")


def get_admin_organization_profiles():
    return OrganizationProfile.objects.select_related("created_by", "updated_by").all()


def get_public_leadership_members():
    return LeadershipMember.objects.filter(is_active=True).select_related("created_by", "updated_by")


def get_admin_leadership_members():
    return LeadershipMember.objects.select_related("created_by", "updated_by").all()


def get_active_hero_section():
    return HeroSection.objects.filter(is_active=True).select_related("created_by", "updated_by").first()


def get_admin_hero_sections():
    return HeroSection.objects.select_related("created_by", "updated_by").all()


def get_active_about_section():
    return AboutSection.objects.filter(is_active=True).select_related("created_by", "updated_by").first()


def get_admin_about_section():
    return AboutSection.objects.select_related("created_by", "updated_by").order_by("-updated_at").first()


def get_active_cabinet_calendar():
    return CabinetCalendar.objects.filter(is_active=True).select_related("created_by", "updated_by").first()


def get_admin_cabinet_calendar():
    return CabinetCalendar.objects.select_related("created_by", "updated_by").order_by("-updated_at").first()
