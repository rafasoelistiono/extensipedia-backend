from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models

from core.models import BaseModel, SlugModelMixin, image_upload_to
from core.validators import validate_file_size


class CompetencyProgram(SlugModelMixin, BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    poster = models.ImageField(
        upload_to=image_upload_to("competency/programs"),
        blank=True,
        null=True,
        validators=[validate_file_size],
    )
    starts_at = models.DateTimeField(blank=True, null=True)
    ends_at = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class AgendaCard(BaseModel):
    MAX_RECORDS = 15

    class CategoryTag(models.TextChoices):
        WORKSHOP = "workshop", "Workshop"
        LOMBA = "lomba", "Lomba"

    class ScopeTag(models.TextChoices):
        NASIONAL = "nasional", "Nasional"
        INTERNASIONAL = "internasional", "Internasional"

    class PricingTag(models.TextChoices):
        BERBAYAR = "berbayar", "Berbayar"
        TIDAK_BERBAYAR = "tidak berbayar", "Tidak Berbayar"

    title = models.CharField(max_length=255)
    short_description = models.TextField(validators=[MinLengthValidator(500)])
    urgency_tag = models.BooleanField(default=False)
    recommendation_tag = models.BooleanField(default=False)
    category_tag = models.CharField(max_length=100, choices=CategoryTag.choices)
    scope_tag = models.CharField(max_length=100, choices=ScopeTag.choices)
    pricing_tag = models.CharField(max_length=100, choices=PricingTag.choices)
    deadline_date = models.DateField()
    registration_link = models.URLField()
    google_calendar_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at", "-updated_at", "deadline_date", "title"]

    def __str__(self):
        return self.title

    def clean(self):
        queryset = self.__class__.objects.all()
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)
        if queryset.count() >= self.MAX_RECORDS:
            raise ValidationError(
                {"non_field_errors": [f"Competency agenda cards support a maximum of {self.MAX_RECORDS} records."]}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
