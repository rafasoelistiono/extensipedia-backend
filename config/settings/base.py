from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    DJANGO_SECRET_KEY=(str, "change-me"),
    DJANGO_ALLOWED_HOSTS=(list, ["127.0.0.1", "localhost"]),
    DJANGO_CORS_ALLOWED_ORIGINS=(list, []),
    DJANGO_CSRF_TRUSTED_ORIGINS=(list, []),
    DJANGO_DEFAULT_FROM_EMAIL=(str, "noreply@extensipedia.local"),
    DJANGO_EMAIL_BACKEND=(str, "django.core.mail.backends.smtp.EmailBackend"),
    DJANGO_EMAIL_HOST=(str, "smtp.gmail.com"),
    DJANGO_EMAIL_PORT=(int, 587),
    DJANGO_EMAIL_HOST_USER=(str, ""),
    DJANGO_EMAIL_HOST_PASSWORD=(str, ""),
    DJANGO_EMAIL_USE_TLS=(bool, True),
    DJANGO_EMAIL_USE_SSL=(bool, False),
    DJANGO_EMAIL_TIMEOUT=(int, 30),
    JWT_ACCESS_TOKEN_MINUTES=(int, 15),
    JWT_REFRESH_TOKEN_DAYS=(int, 7),
    DATABASE_URL=(
        str,
        "postgresql://postgres:postgres@127.0.0.1:5432/extensipedia",
    ),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])
CORS_ALLOWED_ORIGINS = env.list("DJANGO_CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True
DEFAULT_FROM_EMAIL = env("DJANGO_DEFAULT_FROM_EMAIL")
EMAIL_BACKEND = env("DJANGO_EMAIL_BACKEND")
EMAIL_HOST = env("DJANGO_EMAIL_HOST")
EMAIL_PORT = env.int("DJANGO_EMAIL_PORT")
EMAIL_HOST_USER = env("DJANGO_EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("DJANGO_EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = env.bool("DJANGO_EMAIL_USE_TLS")
EMAIL_USE_SSL = env.bool("DJANGO_EMAIL_USE_SSL")
EMAIL_TIMEOUT = env.int("DJANGO_EMAIL_TIMEOUT")

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "django_filters",
    "rest_framework",
    "drf_spectacular",
    "rest_framework_simplejwt.token_blacklist",
]

LOCAL_APPS = [
    "core",
    "accounts",
    "about",
    "academic",
    "competency",
    "career",
    "advocacy",
    "aspirations",
    "analytics_dashboard",
    "dashboard",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "analytics_dashboard.middleware.PublicVisitorAnalyticsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": env.db("DATABASE_URL"),
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Bangkok"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

FILE_UPLOAD_PERMISSIONS = 0o644
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "dashboard:login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "dashboard:login"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardResultsSetPagination",
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "PAGE_SIZE": 10,
    "DEFAULT_RENDERER_CLASSES": (
        "core.renderers.StandardJSONRenderer",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
    "DEFAULT_THROTTLE_RATES": {
        "aspiration_submit_burst": "2/hour",
        "aspiration_submit_sustained": "5/day",
        "aspiration_interaction_burst": "10/hour",
        "aspiration_interaction_sustained": "30/day",
        "ticket_tracking": "60/hour",
        "admin_login_burst": "5/min",
        "admin_login_sustained": "20/hour",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_ACCESS_TOKEN_MINUTES")),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_TOKEN_DAYS")),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Extensipedia API",
    "DESCRIPTION": "Campus/organization backend API for public and admin clients.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "ENUM_NAME_OVERRIDES": {
        "AspirationSubmissionStatusEnum": "aspirations.models.AspirationSubmission.Status",
        "AspirationSubmissionVisibilityEnum": "aspirations.models.AspirationSubmission.Visibility",
    },
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": True,
    },
}
