from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.db import models

from competency.constants import DEFAULT_LOMBA_CARI_TIM_LINK
from core.models import BaseModel, SlugModelMixin, image_upload_to
from core.validators import validate_file_size, validate_image_extension


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
    MAX_RECORDS = 100

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
    short_description = models.TextField(validators=[MaxLengthValidator(300)])
    urgency_tag = models.BooleanField(default=False)
    recommendation_tag = models.BooleanField(default=False)
    category_tag = models.CharField(max_length=100, choices=CategoryTag.choices)
    scope_tag = models.CharField(max_length=100, choices=ScopeTag.choices)
    pricing_tag = models.CharField(max_length=100, choices=PricingTag.choices)
    deadline_date = models.DateField()
    registration_link = models.URLField()
    team_finding_link = models.URLField(blank=True)
    google_calendar_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at", "-updated_at", "deadline_date", "title"]

    def __str__(self):
        return self.title

    def clean(self):
        if self.category_tag == self.CategoryTag.LOMBA and not self.team_finding_link:
            self.team_finding_link = DEFAULT_LOMBA_CARI_TIM_LINK
        elif self.category_tag != self.CategoryTag.LOMBA:
            self.team_finding_link = ""

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


class CompetencyWinnerSlide(BaseModel):
    MAX_RECORDS = 5
    SLOT_CHOICES = tuple((index, f"Slot {index}") for index in range(1, MAX_RECORDS + 1))

    image = models.ImageField(
        upload_to=image_upload_to("competency/winner-slides"),
        blank=True,
        null=True,
        validators=[validate_file_size, validate_image_extension],
    )
    alt_text = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveSmallIntegerField(choices=SLOT_CHOICES, unique=True)

    class Meta:
        ordering = ["display_order", "-updated_at"]

    def __str__(self):
        return f"Winner Slide Slot {self.display_order}"

    def clean(self):
        errors = {}
        queryset = self.__class__.objects.all()
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)

        if queryset.count() >= self.MAX_RECORDS:
            errors["display_order"] = f"Winner slides support a maximum of {self.MAX_RECORDS} records."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.alt_text:
            self.alt_text = f"Winner slide slot {self.display_order}"
        self.full_clean()
        super().save(*args, **kwargs)
