from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.selectors import get_user_list_queryset
from accounts.permissions import IsAdminPanelUser, IsSuperAdminUser
from accounts.serializers import (
    AdminLoginSerializer,
    AdminLogoutSerializer,
    AdminTokenRefreshSerializer,
    AdminUserSerializer,
    CurrentUserSerializer,
)
from accounts.throttles import AdminLoginBurstThrottle, AdminLoginSustainedThrottle
from core.mixins import AdminCrudEndpointMixin
from core.responses import success_response


class CurrentAdminProfileView(APIView):
    permission_classes = [IsAdminPanelUser]
    serializer_class = CurrentUserSerializer

    def get(self, request):
        serializer = CurrentUserSerializer(request.user, context={"request": request})
        return success_response(serializer.data, message="Current admin profile retrieved successfully")


class AdminLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = AdminLoginSerializer
    throttle_classes = [AdminLoginBurstThrottle, AdminLoginSustainedThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return success_response(serializer.validated_data, message="Authentication successful")


class AdminTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    serializer_class = AdminTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return success_response(serializer.validated_data, message="Token refreshed successfully")


class AdminLogoutView(generics.GenericAPIView):
    permission_classes = [IsAdminPanelUser]
    serializer_class = AdminLogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=None, message="Logout successful")


class AdminUserViewSet(AdminCrudEndpointMixin):
    serializer_class = AdminUserSerializer
    permission_classes = [IsSuperAdminUser]
    filterset_fields = ("is_active", "is_staff", "is_superuser")
    search_fields = ("email", "full_name")
    ordering_fields = ("full_name", "email", "created_at", "updated_at")
    ordering = ("full_name", "email")

    def get_queryset(self):
        return get_user_list_queryset()
