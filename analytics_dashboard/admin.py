from django.contrib import admin

from analytics_dashboard.models import ActivityEvent, ActivityEventCounter, VisitorDailyVisit

admin.site.register(VisitorDailyVisit)
admin.site.register(ActivityEventCounter)
admin.site.register(ActivityEvent)
