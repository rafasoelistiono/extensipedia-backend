from django.db import models

from core.models import BaseModel, SlugModelMixin, image_upload_to
from core.validators import validate_embed_url, validate_file_size


class AdvocacyCampaign(SlugModelMixin, BaseModel):
    title = models.CharField(max_length=255)
    summary = models.TextField()
    content = models.TextField(blank=True)
    banner = models.ImageField(
        upload_to=image_upload_to("advocacy/campaigns"),
        blank=True,
        null=True,
        validators=[validate_file_size],
    )
    embed_url = models.URLField(blank=True, validators=[validate_embed_url])
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title
