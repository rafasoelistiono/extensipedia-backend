from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (  # noqa: F405
    "core.renderers.StandardJSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
)
