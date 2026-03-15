from django.contrib import admin

from about.models import AboutSection, CabinetCalendar, HeroSection, LeadershipMember, OrganizationProfile

admin.site.register(OrganizationProfile)
admin.site.register(LeadershipMember)
admin.site.register(HeroSection)
admin.site.register(AboutSection)
admin.site.register(CabinetCalendar)
