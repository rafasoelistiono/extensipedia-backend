from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect


class DashboardAccessRequiredMixin(LoginRequiredMixin):
    login_url = "dashboard:login"
    required_dashboard_sections = ()

    def get_required_dashboard_sections(self):
        if self.required_dashboard_sections:
            return tuple(self.required_dashboard_sections)
        sidebar_section = getattr(self, "sidebar_section", "")
        sidebar_subsection = getattr(self, "sidebar_subsection", "")

        if sidebar_section == "dashboard":
            return ("dashboard",)
        if sidebar_section == "about":
            return ("about",)
        if sidebar_section == "academic":
            return ("academic",)
        if sidebar_section == "profile":
            return ("profile",)
        if sidebar_section == "competency-career":
            return (sidebar_subsection,) if sidebar_subsection else ()
        if sidebar_section == "advocacy":
            return (sidebar_subsection,) if sidebar_subsection else ()
        return ()

    def has_dashboard_access(self):
        user = self.request.user
        if not (user and user.is_authenticated and user.can_access_admin_panel):
            return False
        return all(user.can_access_dashboard_section(section) for section in self.get_required_dashboard_sections())

    def handle_no_permission(self):
        if self.request.user.is_authenticated and self.request.user.can_access_admin_panel:
            raise PermissionDenied("You do not have access to this dashboard section.")
        return super().handle_no_permission()

    def dispatch(self, request, *args, **kwargs):
        if not self.has_dashboard_access():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class DashboardPageMixin(DashboardAccessRequiredMixin):
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
        context.setdefault("allowed_dashboard_sections", tuple(self.request.user.dashboard_allowed_sections))
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


class PostActionMessageMixin(DashboardAccessRequiredMixin):
    success_message = ""

    def post(self, request, *args, **kwargs):
        response = self.handle_action(request, *args, **kwargs)
        if self.success_message:
            messages.success(request, self.success_message)
        return response

    def handle_action(self, request, *args, **kwargs):
        raise NotImplementedError
