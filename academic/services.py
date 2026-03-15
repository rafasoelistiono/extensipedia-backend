from django.shortcuts import get_object_or_404

from academic.models import RepositoryMaterial, YouTubeSection
from academic.selectors import get_repository_materials


def build_repository_grouped_payload(serializer_class):
    queryset = get_repository_materials()
    grouped = {
        RepositoryMaterial.Sections.AKUNTANSI: [],
        RepositoryMaterial.Sections.MANAJEMEN: [],
    }

    for item in queryset:
        grouped[item.section].append(serializer_class(item).data)

    return {
        "akuntansi": grouped[RepositoryMaterial.Sections.AKUNTANSI],
        "manajemen": grouped[RepositoryMaterial.Sections.MANAJEMEN],
    }


def get_active_youtube_section_or_404():
    return get_object_or_404(YouTubeSection, is_active=True)
