from django.db import models
from django.db.models import Q

from core.models import BaseModel, SingleActiveConfigurationMixin


class CareerOpportunity(BaseModel):
    title = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    description = models.TextField()
    apply_url = models.URLField(blank=True)
    closes_at = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} - {self.organization}"


class CareerResourceConfiguration(SingleActiveConfigurationMixin, BaseModel):
    cv_templates = models.URLField()
    cover_letter = models.URLField()
    portfolio_guide = models.URLField()
    salary_script = models.URLField()
    case_study_interview_prep = models.URLField()

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],
                condition=Q(is_active=True),
                name="unique_active_career_resource_configuration",
            )
        ]

    def __str__(self):
        return "Career Resources"
