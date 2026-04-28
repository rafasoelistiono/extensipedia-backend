from academic.models import (
    AcademicDigitalResourceConfiguration,
    AcademicService,
    CountdownEvent,
    QuickDownloadItem,
    RepositoryMaterial,
    YouTubeSection,
)


def get_public_academic_services():
    return AcademicService.objects.filter(is_published=True).select_related("created_by", "updated_by")


def get_admin_academic_services():
    return AcademicService.objects.select_related("created_by", "updated_by").all()


def get_public_quick_download_items():
    return QuickDownloadItem.objects.filter(is_active=True).select_related("created_by", "updated_by").all()


def get_admin_quick_download_items():
    return QuickDownloadItem.objects.select_related("created_by", "updated_by").all()


def get_repository_materials():
    return RepositoryMaterial.objects.select_related("created_by", "updated_by").all()


def get_public_active_youtube_section():
    return YouTubeSection.objects.filter(is_active=True).select_related("created_by", "updated_by").first()


def get_admin_youtube_sections():
    return YouTubeSection.objects.select_related("created_by", "updated_by").all()


def get_public_countdown_events():
    return CountdownEvent.objects.filter(is_active=True).select_related("created_by", "updated_by").all()


def get_admin_countdown_events():
    return CountdownEvent.objects.select_related("created_by", "updated_by").all()


def get_admin_academic_digital_resource_configurations():
    return AcademicDigitalResourceConfiguration.objects.select_related("created_by", "updated_by").all()
