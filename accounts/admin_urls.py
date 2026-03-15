from django.urls import path
from rest_framework.routers import SimpleRouter

from accounts.views import (
    AdminLoginView,
    AdminLogoutView,
    AdminTokenRefreshView,
    AdminUserViewSet,
    CurrentAdminProfileView,
)

router = SimpleRouter()
router.register("users", AdminUserViewSet, basename="admin-users")

urlpatterns = [
    path("auth/login/", AdminLoginView.as_view(), name="admin-login"),
    path("auth/refresh/", AdminTokenRefreshView.as_view(), name="admin-refresh"),
    path("auth/logout/", AdminLogoutView.as_view(), name="admin-logout"),
    path("profile/", CurrentAdminProfileView.as_view(), name="admin-profile"),
]
urlpatterns += router.urls
