from rest_framework.permissions import BasePermission


class IsAdminPanelUser(BasePermission):
    message = "You do not have permission to access the admin API."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_active and user.is_staff)


class IsSuperAdminUser(BasePermission):
    message = "Only superadmin users can perform this action."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_active and user.is_superuser)
