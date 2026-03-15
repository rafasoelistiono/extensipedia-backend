from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.managers import UserManager
from core.models import BaseModel, image_upload_to
from core.validators import validate_file_size


class User(BaseModel, AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "admin", "Admin"
        SUPERADMIN = "superadmin", "Superadmin"

    username = None
    email = models.EmailField(unique=True)
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
        return self.full_name or self.email

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
