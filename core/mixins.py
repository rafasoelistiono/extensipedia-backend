from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny

from accounts.permissions import IsAdminPanelUser

from core.responses import success_response


class MessageWrappedMixin:
    list_message = "Resources retrieved successfully"
    retrieve_message = "Resource retrieved successfully"
    create_message = "Resource created successfully"
    update_message = "Resource updated successfully"
    partial_update_message = "Resource updated successfully"
    destroy_message = "Resource deleted successfully"

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response._message = self.list_message
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        response._message = self.retrieve_message
        return response

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return success_response(
            serializer.data,
            message=self.create_message,
            status_code=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(serializer.data, message=self.update_message)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(data=None, message=self.destroy_message)


class AuditFieldsMixin:
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(created_by=self.request.user, updated_by=self.request.user)
            return
        serializer.save()

    def perform_update(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(updated_by=self.request.user)
            return
        serializer.save()


class PublicReadOnlyEndpointMixin(MessageWrappedMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]


class AdminCrudEndpointMixin(AuditFieldsMixin, MessageWrappedMixin, viewsets.ModelViewSet):
    permission_classes = [IsAdminPanelUser]
