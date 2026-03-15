from django.contrib import admin

from academic.models import AcademicService, CountdownEvent, QuickDownloadItem, RepositoryMaterial, YouTubeSection

admin.site.register(AcademicService)
admin.site.register(QuickDownloadItem)
admin.site.register(RepositoryMaterial)
admin.site.register(YouTubeSection)
admin.site.register(CountdownEvent)
