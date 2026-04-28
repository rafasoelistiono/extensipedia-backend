from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.managers import UserManager
from core.models import BaseModel, image_upload_to
from core.validators import validate_file_size


class User(BaseModel, AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "admin", "Admin"
        SUPERADMIN = "superadmin", "Superadmin"

    class DashboardAccessScopes(models.TextChoices):
        FULL = "full", "Superadmin"
        ACADEMIC = "academic", "Akademik"
        COMPETENCY = "competency", "Kompetensi"
        ADVOCACY = "advocacy", "Advokasi"

    DASHBOARD_SECTION_ACCESS = {
        DashboardAccessScopes.FULL: (
            "dashboard",
            "about",
            "academic",
            "competency",
            "career",
            "aspirations",
            "tickets",
            "advocacy_resources",
            "profile",
        ),
        DashboardAccessScopes.ACADEMIC: ("dashboard", "about", "academic", "profile"),
        DashboardAccessScopes.COMPETENCY: ("dashboard", "about", "competency", "career", "profile"),
        DashboardAccessScopes.ADVOCACY: ("dashboard", "about", "aspirations", "tickets", "advocacy_resources", "profile"),
    }

    username = None
    email = models.EmailField(unique=True)
    dashboard_username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    dashboard_access_scope = models.CharField(
        max_length=20,
        choices=DashboardAccessScopes.choices,
        default=DashboardAccessScopes.FULL,
    )
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(
        upload_to=image_upload_to("accounts/avatars"),
        blank=True,
        null=True,
        validators=[validate_file_size],
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ["full_name", "email"]

    def __str__(self):
        return self.full_name or self.dashboard_username or self.email

    @property
    def role(self):
        if self.is_superuser:
            return self.Roles.SUPERADMIN
        if self.is_staff:
            return self.Roles.ADMIN
        return None

    @property
    def can_access_admin_panel(self):
        return self.is_active and self.is_staff

    @property
    def dashboard_role_label(self):
        if self.is_superuser:
            return self.Roles.SUPERADMIN.label
        return self.get_dashboard_access_scope_display() or self.Roles.ADMIN.label

    @property
    def dashboard_allowed_sections(self):
        scope = self.dashboard_access_scope or self.DashboardAccessScopes.FULL
        return self.DASHBOARD_SECTION_ACCESS.get(scope, self.DASHBOARD_SECTION_ACCESS[self.DashboardAccessScopes.FULL])

    def can_access_dashboard_section(self, section):
        if not section:
            return True
        return self.can_access_admin_panel and section in self.dashboard_allowed_sections

    def save(self, *args, **kwargs):
        if not self.dashboard_username:
            base_username = (self.email or "").split("@", 1)[0] or "user"
            candidate = base_username
            suffix = 1
            while type(self).objects.exclude(pk=self.pk).filter(dashboard_username=candidate).exists():
                candidate = f"{base_username}{suffix}"
                suffix += 1
            self.dashboard_username = candidate
        super().save(*args, **kwargs)
