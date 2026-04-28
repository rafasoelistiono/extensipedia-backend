from django.contrib import admin

from advocacy.models import AdvocacyCampaign, AdvocacyPolicyResourceConfiguration

admin.site.register(AdvocacyCampaign)
admin.site.register(AdvocacyPolicyResourceConfiguration)
