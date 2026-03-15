from django.shortcuts import get_object_or_404

from about.models import AboutSection, HeroSection


def get_active_hero_or_404():
    return get_object_or_404(HeroSection, is_active=True)


def get_active_about_section_or_404():
    return get_object_or_404(AboutSection, is_active=True)
