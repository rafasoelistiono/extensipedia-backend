from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseModel
from core.validators import validate_file_size, validate_image_or_pdf_extension


class AspirationSubmission(BaseModel):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        INVESTIGATING = "investigating", "Investigating"
        RESOLVED = "resolved", "Resolved"

    class Visibility(models.TextChoices):
        PUBLIC = "public", "Public"
        ANONYMOUS = "anonymous", "Anonymous"

    MAX_FEATURED = 6

    full_name = models.CharField(max_length=255)
    npm = models.CharField(max_length=50)
    email = models.EmailField()
    title = models.CharField(max_length=255)
    short_description = models.TextField()
    evidence_attachment = models.FileField(
        upload_to="aspirations/evidence/",
        blank=True,
        null=True,
        validators=[validate_file_size, validate_image_or_pdf_extension],
    )
    ticket_id = models.CharField(max_length=32, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.ANONYMOUS)
    is_featured = models.BooleanField(default=False)
    upvote_count = models.PositiveIntegerField(default=0)
    vote_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ticket_id} - {self.title}"

    def clean(self):
        if self.is_featured:
            featured_count = self.__class__.objects.filter(is_featured=True)
            if self.pk:
                featured_count = featured_count.exclude(pk=self.pk)
            if featured_count.count() >= self.MAX_FEATURED:
                raise ValidationError({"is_featured": f"Only {self.MAX_FEATURED} aspirations can be featured at a time."})

            if self.status == self.Status.SUBMITTED:
                raise ValidationError({"status": "Only investigating or resolved aspirations can be featured publicly."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class AspirationActivityLog(BaseModel):
    class Action(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        UPDATED = "updated", "Updated"
        FEATURED = "featured", "Featured"
        UNFEATURED = "unfeatured", "Unfeatured"

    aspiration = models.ForeignKey(
        AspirationSubmission,
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    message = models.CharField(max_length=255)
    actor_name = models.CharField(max_length=255, blank=True)
    status_snapshot = models.CharField(max_length=20, choices=AspirationSubmission.Status.choices)
    visibility_snapshot = models.CharField(max_length=20, choices=AspirationSubmission.Visibility.choices)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.aspiration.ticket_id} - {self.action}"
