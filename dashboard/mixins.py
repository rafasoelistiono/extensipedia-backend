from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect


class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "dashboard:login"

    def test_func(self):
        return bool(self.request.user.is_authenticated and self.request.user.is_superuser)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("Only superadmin users can access this page.")
        return super().handle_no_permission()


class DashboardPageMixin(SuperuserRequiredMixin):
    page_title = ""
    page_heading = ""
    page_description = ""
    sidebar_section = ""
    sidebar_subsection = ""
    breadcrumbs = None

    def get_breadcrumbs(self):
        return self.breadcrumbs or []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("page_title", self.page_title)
        context.setdefault("page_heading", self.page_heading or self.page_title)
        context.setdefault("page_description", self.page_description)
        context.setdefault("sidebar_section", self.sidebar_section)
        context.setdefault("sidebar_subsection", self.sidebar_subsection)
        context.setdefault("breadcrumbs", self.get_breadcrumbs())
        return context


class SuccessMessageMixin:
    success_message = "Data saved successfully."

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class DeleteMessageMixin:
    success_message = "Data deleted successfully."

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, self.success_message)
        return response


class PostActionMessageMixin(SuperuserRequiredMixin):
    success_message = ""

    def post(self, request, *args, **kwargs):
        response = self.handle_action(request, *args, **kwargs)
        if self.success_message:
            messages.success(request, self.success_message)
        return response

    def handle_action(self, request, *args, **kwargs):
        raise NotImplementedError
