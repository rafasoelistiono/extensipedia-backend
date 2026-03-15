import os
import uuid

from django.conf import settings
from django.db import models, transaction
from django.utils.deconstruct import deconstructible
from django.utils.text import slugify


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
    )

    class Meta:
        abstract = True


class SingleActiveConfigurationMixin(models.Model):
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.is_active:
                queryset = self.__class__.objects.filter(is_active=True)
                if self.pk:
                    queryset = queryset.exclude(pk=self.pk)
                queryset.update(is_active=False)
            super().save(*args, **kwargs)


class SlugModelMixin(models.Model):
    slug = models.SlugField(unique=True, max_length=255)
    slug_source_field = "title"

    class Meta:
        abstract = True

    def generate_slug_value(self):
        source_value = getattr(self, self.slug_source_field, "") or self.__class__.__name__
        base_slug = slugify(source_value) or uuid.uuid4().hex[:12]
        slug = base_slug
        model_class = self.__class__
        suffix = 1

        while model_class.objects.exclude(pk=self.pk).filter(slug=slug).exists():
            slug = f"{base_slug}-{suffix}"
            suffix += 1

        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug_value()
        super().save(*args, **kwargs)


@deconstructible
class UploadToPath:
    def __init__(self, base_folder):
        self.base_folder = base_folder

    def __call__(self, instance, filename):
        extension = os.path.splitext(filename)[1].lower()
        model_name = instance.__class__.__name__.lower()
        return f"{self.base_folder}/{model_name}/{instance.pk or uuid.uuid4()}{extension}"


def image_upload_to(base_folder):
    return UploadToPath(base_folder)
