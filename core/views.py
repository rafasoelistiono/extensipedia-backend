from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from core.responses import success_response
from core.serializers import ApiRootSerializer, HealthCheckSerializer


class ApiRootView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ApiRootSerializer

    @extend_schema(responses=ApiRootSerializer)
    def get(self, request):
        return success_response(
            {
                "name": "Extensipedia API",
                "version": "v1",
                "public_base_url": request.build_absolute_uri("/api/v1/public/"),
                "admin_base_url": request.build_absolute_uri("/api/v1/admin/"),
            },
            message="Extensipedia API v1",
        )


class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    serializer_class = HealthCheckSerializer

    def get(self, request):
        return success_response({"status": "ok"}, message="Service is healthy")
