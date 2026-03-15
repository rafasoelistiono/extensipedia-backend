from django.contrib import admin

from aspirations.models import AspirationActivityLog, AspirationSubmission

admin.site.register(AspirationSubmission)
admin.site.register(AspirationActivityLog)
