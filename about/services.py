from django.shortcuts import get_object_or_404

from about.models import AboutSection, CabinetCalendar, HeroSection


def get_active_hero_or_404():
    return get_object_or_404(HeroSection, is_active=True)


def get_active_about_section_or_404():
    return get_object_or_404(AboutSection, is_active=True)


def get_active_cabinet_calendar_or_404():
    return get_object_or_404(CabinetCalendar, is_active=True)


def get_or_build_about_section():
    return (
        AboutSection.objects.filter(is_active=True).first()
        or AboutSection.objects.order_by("-updated_at").first()
        or AboutSection(is_active=True)
    )


def get_or_build_cabinet_calendar():
    return (
        CabinetCalendar.objects.filter(is_active=True).first()
        or CabinetCalendar.objects.order_by("-updated_at").first()
        or CabinetCalendar(is_active=True)
    )
