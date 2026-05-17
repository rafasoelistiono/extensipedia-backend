from django.db import models
from django.db.models import Q

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


class ActivityActionKey(models.TextChoices):
    HOME_HERO_ACCESS_ACADEMIC = "home.hero.access_academic", "Home hero access academic"
    HOME_HERO_INFO_COMPETITION = "home.hero.info_competition", "Home hero info competition"
    HOME_ABOUT_ACCESS_ACADEMIC = "home.about.access_academic", "Home about access academic"
    HOME_ABOUT_INFO_COMPETITION = "home.about.info_competition", "Home about info competition"
    HOME_FEATURES_ACADEMIC_ACCESS_NOW = "home.features.academic.access_now", "Home features academic access now"
    HOME_FEATURES_COMPETENCY_EXPLORE = "home.features.competency.explore", "Home features competency explore"
    HOME_FEATURES_CAREER_VIEW_RESOURCE = "home.features.career.view_resource", "Home features career view resource"
    HOME_FEATURES_ADVOCACY_SUBMIT_ASPIRATION = (
        "home.features.advocacy.submit_aspiration",
        "Home features advocacy submit aspiration",
    )
    HOME_COMPETENCY_VIEW_ALL = "home.competency.view_all", "Home competency view all"
    HOME_COMPETENCY_REGISTER = "home.competency.register", "Home competency register"
    HOME_COMPETENCY_FIND_TEAM = "home.competency.find_team", "Home competency find team"
    HOME_COMPETENCY_ADD_CALENDAR = "home.competency.add_calendar", "Home competency add calendar"
    HOME_ASPIRATION_FILTER_ALL = "home.aspiration.filter_all", "Home aspiration filter all"
    HOME_ASPIRATION_FILTER_PUBLIC = "home.aspiration.filter_public", "Home aspiration filter public"
    HOME_ASPIRATION_FILTER_ANONYMOUS = "home.aspiration.filter_anonymous", "Home aspiration filter anonymous"
    HOME_ASPIRATION_UPVOTE = "home.aspiration.upvote", "Home aspiration upvote"
    HOME_ASPIRATION_DOWNVOTE = "home.aspiration.downvote", "Home aspiration downvote"
    HOME_TICKET_TRACK = "home.ticket.track", "Home ticket track"
    HOME_TICKET_VIEW_FORM = "home.ticket.view_form", "Home ticket view form"


class ActivityEventCounter(BaseModel):
    action_key = models.CharField(max_length=120, choices=ActivityActionKey.choices, unique=True)
    total_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["action_key"]

    def __str__(self):
        return f"{self.action_key}: {self.total_count}"


class ActivityEvent(BaseModel):
    counter = models.ForeignKey(ActivityEventCounter, on_delete=models.CASCADE, related_name="events")
    action_key = models.CharField(max_length=120, choices=ActivityActionKey.choices)
    label = models.CharField(max_length=120)
    page_path = models.CharField(max_length=255)
    target_type = models.CharField(max_length=64)
    target_id = models.CharField(max_length=64, blank=True, null=True)
    target_url = models.CharField(max_length=1000, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=120, blank=True, null=True)
    session_key = models.CharField(max_length=64, blank=True)
    user_hash = models.CharField(max_length=64, blank=True)
    ip_hash = models.CharField(max_length=64, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["action_key", "idempotency_key"],
                condition=Q(idempotency_key__isnull=False),
                name="unique_activity_event_idempotency_key",
            )
        ]

    def __str__(self):
        return f"{self.action_key} - {self.created_at:%Y-%m-%d %H:%M:%S}"
