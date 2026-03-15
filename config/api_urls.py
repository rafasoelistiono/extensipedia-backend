from django.urls import include, path

from about.urls import admin_urlpatterns as about_admin_urlpatterns
from about.urls import public_urlpatterns as about_public_urlpatterns
from academic.urls import admin_urlpatterns as academic_admin_urlpatterns
from academic.urls import public_urlpatterns as academic_public_urlpatterns
from accounts.urls import admin_urlpatterns as accounts_admin_urlpatterns
from accounts.urls import public_urlpatterns as accounts_public_urlpatterns
from advocacy.urls import admin_urlpatterns as advocacy_admin_urlpatterns
from advocacy.urls import public_urlpatterns as advocacy_public_urlpatterns
from analytics_dashboard.urls import admin_urlpatterns as analytics_admin_urlpatterns
from analytics_dashboard.urls import public_urlpatterns as analytics_public_urlpatterns
from aspirations.urls import admin_urlpatterns as aspirations_admin_urlpatterns
from aspirations.urls import public_urlpatterns as aspirations_public_urlpatterns
from aspirations.ticket_public_urls import urlpatterns as tickets_public_urlpatterns
from career.urls import admin_urlpatterns as career_admin_urlpatterns
from career.urls import public_urlpatterns as career_public_urlpatterns
from competency.urls import admin_urlpatterns as competency_admin_urlpatterns
from competency.urls import public_urlpatterns as competency_public_urlpatterns
from core.urls import public_urlpatterns as core_public_urlpatterns
from core.views import ApiRootView

urlpatterns = [
    path("", ApiRootView.as_view(), name="api-root"),
    path("public/core/", include((core_public_urlpatterns, "core"), namespace="public-core")),
    path("public/accounts/", include((accounts_public_urlpatterns, "accounts"), namespace="public-accounts")),
    path("public/about/", include((about_public_urlpatterns, "about"), namespace="public-about")),
    path("public/academic/", include((academic_public_urlpatterns, "academic"), namespace="public-academic")),
    path(
        "public/competency/",
        include((competency_public_urlpatterns, "competency"), namespace="public-competency"),
    ),
    path("public/career/", include((career_public_urlpatterns, "career"), namespace="public-career")),
    path("public/advocacy/", include((advocacy_public_urlpatterns, "advocacy"), namespace="public-advocacy")),
    path(
        "public/aspirations/",
        include((aspirations_public_urlpatterns, "aspirations"), namespace="public-aspirations"),
    ),
    path("public/tickets/", include((tickets_public_urlpatterns, "tickets"), namespace="public-tickets")),
    path(
        "public/analytics-dashboard/",
        include((analytics_public_urlpatterns, "analytics_dashboard"), namespace="public-analytics-dashboard"),
    ),
    path("admin/accounts/", include((accounts_admin_urlpatterns, "accounts"), namespace="admin-accounts")),
    path("admin/about/", include((about_admin_urlpatterns, "about"), namespace="admin-about")),
    path("admin/academic/", include((academic_admin_urlpatterns, "academic"), namespace="admin-academic")),
    path(
        "admin/competency/",
        include((competency_admin_urlpatterns, "competency"), namespace="admin-competency"),
    ),
    path("admin/career/", include((career_admin_urlpatterns, "career"), namespace="admin-career")),
    path("admin/advocacy/", include((advocacy_admin_urlpatterns, "advocacy"), namespace="admin-advocacy")),
    path(
        "admin/aspirations/",
        include((aspirations_admin_urlpatterns, "aspirations"), namespace="admin-aspirations"),
    ),
    path(
        "admin/dashboard/",
        include((analytics_admin_urlpatterns, "analytics_dashboard"), namespace="admin-dashboard"),
    ),
]
