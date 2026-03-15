from django.db import models
from django.db.models import Q

from core.models import BaseModel, SingleActiveConfigurationMixin, image_upload_to
from core.validators import (
    validate_embed_url,
    validate_file_size,
    validate_iframe_or_embed_input,
)

class OrganizationProfile(BaseModel):
    name = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255, blank=True)
    summary = models.TextField()
    vision = models.TextField(blank=True)
    mission = models.TextField(blank=True)
    logo = models.ImageField(
        upload_to=image_upload_to("about/logos"),
        blank=True,
        null=True,
        validators=[validate_file_size],
    )
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class LeadershipMember(BaseModel):
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    photo = models.ImageField(
        upload_to=image_upload_to("about/leaders"),
        blank=True,
        null=True,
        validators=[validate_file_size],
    )
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return f"{self.name} - {self.role}"


class HeroSection(SingleActiveConfigurationMixin, BaseModel):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to=image_upload_to("about/hero"),
        blank=True,
        null=True,
        validators=[validate_file_size],
    )
    primary_button_label = models.CharField(max_length=100, blank=True)
    primary_button_url = models.URLField(blank=True)
    secondary_button_label = models.CharField(max_length=100, blank=True)
    secondary_button_url = models.URLField(blank=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],
                condition=Q(is_active=True),
                name="unique_active_hero_section",
            )
        ]

    def __str__(self):
        return self.title


class AboutSection(SingleActiveConfigurationMixin, BaseModel):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    image = models.ImageField(
        upload_to=image_upload_to("about/sections"),
        blank=True,
        null=True,
        validators=[validate_file_size],
    )

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],
                condition=Q(is_active=True),
                name="unique_active_about_section",
            )
        ]

    def __str__(self):
        return self.title


class CabinetCalendar(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    embed_url = models.URLField(blank=True, validators=[validate_embed_url])
    embed_code = models.TextField(blank=True)
    sanitized_embed_url = models.URLField(editable=False, max_length=1000)
    provider = models.CharField(max_length=100, editable=False, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "-updated_at", "title"]

    def __str__(self):
        return self.title

    def clean(self):
        self.sanitized_embed_url = validate_iframe_or_embed_input(self.embed_url, self.embed_code)
        self.provider = self.detect_provider(self.sanitized_embed_url)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @staticmethod
    def detect_provider(embed_url):
        if "calendar.google.com" in embed_url:
            return "google_calendar"
        if "youtube.com" in embed_url or "youtu.be" in embed_url:
            return "youtube"
        if "vimeo.com" in embed_url:
            return "vimeo"
        if "google.com" in embed_url:
            return "google"
        return "external"
