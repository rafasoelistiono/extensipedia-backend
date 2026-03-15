from django.db import models

from core.models import BaseModel


class VisitorDailyVisit(BaseModel):
    visit_date = models.DateField()
    fingerprint_hash = models.CharField(max_length=64)
    first_path = models.CharField(max_length=255, blank=True)
    hit_count = models.PositiveIntegerField(default=1)
    last_seen_at = models.DateTimeField()

    class Meta:
        ordering = ["-visit_date", "-last_seen_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["visit_date", "fingerprint_hash"],
                name="unique_daily_visitor_fingerprint",
            )
        ]

    def __str__(self):
        return f"{self.visit_date} - {self.fingerprint_hash[:8]}"
