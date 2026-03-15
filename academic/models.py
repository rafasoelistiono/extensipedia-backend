from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from core.models import BaseModel, SingleActiveConfigurationMixin, SlugModelMixin, image_upload_to
from core.validators import (
    validate_file_size,
    validate_google_drive_url,
    validate_iframe_or_embed_input,
)


class AcademicService(SlugModelMixin, BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.ImageField(
        upload_to=image_upload_to("academic/services"),
        blank=True,
        null=True,
        validators=[validate_file_size],
    )
    published_at = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class QuickDownloadItem(BaseModel):
    MAX_ITEMS = 5

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=image_upload_to("academic/quick-downloads"), blank=True, null=True)
    external_url = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "title"]

    def __str__(self):
        return self.title

    def clean(self):
        if bool(self.file) == bool(self.external_url):
            raise ValidationError("Provide either a file upload or an external URL.")

        if self.file:
            validate_file_size(self.file)

        queryset = self.__class__.objects.all()
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)
        if queryset.count() >= self.MAX_ITEMS:
            raise ValidationError({"non_field_errors": [f"Quick downloads support a maximum of {self.MAX_ITEMS} items."]})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class RepositoryMaterial(BaseModel):
    class Sections(models.TextChoices):
        AKUNTANSI = "akuntansi", "Akuntansi"
        MANAJEMEN = "manajemen", "Manajemen"

    MAX_ITEMS_PER_SECTION = 3

    section = models.CharField(max_length=20, choices=Sections.choices)
    title = models.CharField(max_length=255)
    google_drive_link = models.URLField(validators=[validate_google_drive_url])
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["section", "display_order", "title"]

    def __str__(self):
        return f"{self.get_section_display()} - {self.title}"

    def clean(self):
        queryset = self.__class__.objects.filter(section=self.section)
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)
        if queryset.count() >= self.MAX_ITEMS_PER_SECTION:
            raise ValidationError(
                {"section": f"Section {self.get_section_display()} supports a maximum of {self.MAX_ITEMS_PER_SECTION} items."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class YouTubeSection(SingleActiveConfigurationMixin, BaseModel):
    title = models.CharField(max_length=255, default="YouTube")
    description = models.TextField(blank=True)
    embed_url = models.URLField(blank=True)
    embed_code = models.TextField(blank=True)
    sanitized_embed_url = models.URLField(editable=False, max_length=1000)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],
                condition=Q(is_active=True),
                name="unique_active_academic_youtube_section",
            )
        ]

    def __str__(self):
        return self.title

    def clean(self):
        self.sanitized_embed_url = validate_iframe_or_embed_input(self.embed_url, self.embed_code)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class CountdownEvent(BaseModel):
    title = models.CharField(max_length=255)
    target_datetime = models.DateTimeField()
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "target_datetime", "title"]

    def __str__(self):
        return self.title
