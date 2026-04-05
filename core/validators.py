import os
import re
from urllib.parse import urlparse

from django.core.exceptions import ValidationError

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_DOCUMENT_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_EMBED_HOSTS = {
    "www.youtube.com",
    "youtube.com",
    "youtu.be",
    "player.vimeo.com",
    "www.google.com",
    "calendar.google.com",
}
ALLOWED_GOOGLE_DRIVE_HOSTS = {
    "drive.google.com",
    "docs.google.com",
}
IFRAME_SRC_PATTERN = re.compile(
    r'^\s*<iframe\b[^>]*\bsrc=(["\'])(?P<src>https?://[^"\']+)\1[^>]*>\s*</iframe>\s*$',
    re.IGNORECASE | re.DOTALL,
)


def validate_embed_url(value):
    if not value:
        return value

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValidationError("Embed URL must use http or https and include a valid domain.")

    if parsed.netloc not in ALLOWED_EMBED_HOSTS:
        raise ValidationError("Unsupported embed provider.")
    return value


def extract_iframe_src(value):
    if not value:
        return ""

    match = IFRAME_SRC_PATTERN.match(value.strip())
    if not match:
        raise ValidationError("Embed iframe must contain only a single iframe tag with a valid src URL.")
    return match.group("src")


def validate_iframe_or_embed_input(embed_url="", embed_code=""):
    if not embed_url and not embed_code:
        raise ValidationError("Provide either an embed URL or iframe embed code.")

    resolved_url = embed_url
    if embed_code:
        resolved_url = extract_iframe_src(embed_code)

    validate_embed_url(resolved_url)
    return resolved_url


def validate_google_drive_url(value):
    if not value:
        return value

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or parsed.netloc not in ALLOWED_GOOGLE_DRIVE_HOSTS:
        raise ValidationError("Google Drive link must use drive.google.com or docs.google.com.")
    return value


def validate_file_size(file_obj):
    if file_obj and file_obj.size > MAX_FILE_SIZE:
        raise ValidationError("File size must not exceed 5 MB.")
    return file_obj


def validate_image_or_pdf_extension(file_obj):
    extension = os.path.splitext(file_obj.name)[1].lower()
    if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValidationError("Only image files (.jpg, .jpeg, .png, .webp) or .pdf are allowed.")
    return file_obj


def validate_image_extension(file_obj):
    extension = os.path.splitext(file_obj.name)[1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("Only image files (.jpg, .jpeg, .png, .webp) are allowed.")
    return file_obj
