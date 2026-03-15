from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, FormView, ListView, TemplateView, UpdateView

from about.models import AboutSection, CabinetCalendar
from academic.models import CountdownEvent, QuickDownloadItem, RepositoryMaterial, YouTubeSection
from analytics_dashboard.services import build_dashboard_summary, build_recent_ticket_log
from aspirations.models import AspirationSubmission
from aspirations.services import set_featured_state, update_aspiration_submission
from career.models import CareerResourceConfiguration
from competency.models import AgendaCard
from dashboard.forms import (
    AboutSectionForm,
    AgendaCardForm,
    AspirationUpdateForm,
    CabinetCalendarForm,
    CareerResourceConfigurationForm,
    CountdownEventForm,
    DashboardLoginForm,
    QuickDownloadForm,
    RepositoryMaterialForm,
    TicketSearchForm,
    YouTubeSectionForm,
)
from dashboard.mixins import DashboardPageMixin, DeleteMessageMixin, PostActionMessageMixin, SuccessMessageMixin


def apply_audit_fields(instance, user):
    if not instance.pk and not instance.created_by_id:
        instance.created_by = user
    instance.updated_by = user
    return instance


def get_singleton_instance(model, defaults=None):
    instance = model.objects.filter(is_active=True).first()
    if instance:
        return instance
    instance = model.objects.order_by("-updated_at").first()
    if instance:
        return instance
    return model(**(defaults or {}))


def build_pagination_querystring(request):
    querydict = request.GET.copy()
    querydict.pop("page", None)
    return querydict.urlencode()


class AdminRootRedirectView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return redirect("dashboard:home")
        if request.user.is_authenticated:
            logout(request)
        return redirect("dashboard:login")


class DashboardLoginView(FormView):
    template_name = "dashboard/login.html"
    form_class = DashboardLoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return redirect("dashboard:home")
        if request.user.is_authenticated:
            logout(request)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        login(self.request, form.get_user())
        return redirect(self.get_success_url())

    def get_success_url(self):
        return self.request.GET.get("next") or reverse("dashboard:home")


class DashboardLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Anda berhasil keluar dari dashboard admin.")
        return redirect("dashboard:login")


class DashboardHomeView(DashboardPageMixin, TemplateView):
    template_name = "dashboard/dashboard_home.html"
    page_title = "Dashboard"
    page_description = "Ringkasan aspirasi, pengunjung, dan navigasi cepat untuk pengelolaan konten."
    sidebar_section = "dashboard"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        summary = build_dashboard_summary()
        context["summary"] = summary["cards"]
        context["daily_visitors"] = summary["charts"]["daily_visitors_last_30_days"]
        context["recent_logs"] = build_recent_ticket_log(limit=10)
        context["quick_links"] = [
            {"title": "Tentang Kami", "url": reverse("dashboard:about"), "description": "Edit section dan kalender kabinet."},
            {"title": "Akademik", "url": reverse("dashboard:academic"), "description": "Kelola quick downloads, repo, YouTube, dan countdown."},
            {"title": "Kompetensi", "url": reverse("dashboard:competency"), "description": "Kelola agenda cards kompetensi."},
            {"title": "Karir", "url": reverse("dashboard:career"), "description": "Kelola resource link karir."},
            {"title": "Aspirasi", "url": reverse("dashboard:aspiration-list"), "description": "Moderasi aspirasi dan featured items."},
            {"title": "Lacak Tiket", "url": reverse("dashboard:ticket-tracking"), "description": "Cari tiket dan monitor progres."},
        ]
        return context


class AboutSettingsView(DashboardPageMixin, TemplateView):
    template_name = "dashboard/about_page.html"
    page_title = "Tentang Kami"
    page_description = "Update konten section Tentang Kami dan kalender kabinet."
    sidebar_section = "about"

    def get_breadcrumbs(self):
        return [("Tentang Kami", None)]

    def get_section_instance(self):
        return get_singleton_instance(AboutSection, defaults={"is_active": True})

    def get_form(self):
        return AboutSectionForm(instance=self.get_section_instance())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("form", self.get_form())
        context["calendar_items"] = CabinetCalendar.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        instance = self.get_section_instance()
        form = AboutSectionForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            section = form.save(commit=False)
            section.is_active = True
            apply_audit_fields(section, request.user)
            section.save()
            messages.success(request, "Konten Tentang Kami berhasil diperbarui.")
            return redirect("dashboard:about")
        messages.error(request, "Periksa kembali form Tentang Kami.")
        return self.render_to_response(self.get_context_data(form=form))


class DashboardObjectFormMixin(DashboardPageMixin, SuccessMessageMixin):
    template_name = "dashboard/object_form.html"
    cancel_url = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.cancel_url
        context["submit_label"] = getattr(self, "submit_label", "Simpan")
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        apply_audit_fields(self.object, self.request.user)
        self.object.save()
        form.save_m2m()
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())


class DashboardDeleteView(DeleteMessageMixin, DashboardPageMixin, DeleteView):
    template_name = "dashboard/confirm_delete.html"
    cancel_url = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.cancel_url
        return context


class CabinetCalendarCreateView(DashboardObjectFormMixin, CreateView):
    model = CabinetCalendar
    form_class = CabinetCalendarForm
    page_title = "Tambah Kalender Kabinet"
    page_description = "Tambahkan embed/link kalender kabinet baru."
    sidebar_section = "about"
    cancel_url = reverse_lazy("dashboard:about")
    success_url = reverse_lazy("dashboard:about")
    success_message = "Kalender kabinet berhasil ditambahkan."

    def get_breadcrumbs(self):
        return [("Tentang Kami", reverse("dashboard:about")), ("Tambah Kalender", None)]


class CabinetCalendarUpdateView(DashboardObjectFormMixin, UpdateView):
    model = CabinetCalendar
    form_class = CabinetCalendarForm
    page_title = "Edit Kalender Kabinet"
    page_description = "Perbarui detail kalender kabinet."
    sidebar_section = "about"
    cancel_url = reverse_lazy("dashboard:about")
    success_url = reverse_lazy("dashboard:about")
    success_message = "Kalender kabinet berhasil diperbarui."

    def get_breadcrumbs(self):
        return [("Tentang Kami", reverse("dashboard:about")), ("Edit Kalender", None)]


class CabinetCalendarDeleteView(DashboardDeleteView):
    model = CabinetCalendar
    page_title = "Hapus Kalender Kabinet"
    page_description = "Tindakan ini akan menghapus item kalender kabinet."
    sidebar_section = "about"
    cancel_url = reverse_lazy("dashboard:about")
    success_url = reverse_lazy("dashboard:about")
    success_message = "Kalender kabinet berhasil dihapus."

    def get_breadcrumbs(self):
        return [("Tentang Kami", reverse("dashboard:about")), ("Hapus Kalender", None)]


class AcademicOverviewView(DashboardPageMixin, TemplateView):
    template_name = "dashboard/academic_page.html"
    page_title = "Akademik"
    page_description = "Kelola quick download, repository bahan kuliah, YouTube section, dan event countdown."
    sidebar_section = "academic"

    def get_breadcrumbs(self):
        return [("Akademik", None)]

    def get_youtube_instance(self):
        return get_singleton_instance(YouTubeSection, defaults={"title": "YouTube", "is_active": True})

    def get_youtube_form(self):
        return YouTubeSectionForm(instance=self.get_youtube_instance())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("youtube_form", self.get_youtube_form())
        context["quick_downloads"] = QuickDownloadItem.objects.all()
        context["repository_akuntansi"] = RepositoryMaterial.objects.filter(section=RepositoryMaterial.Sections.AKUNTANSI)
        context["repository_manajemen"] = RepositoryMaterial.objects.filter(section=RepositoryMaterial.Sections.MANAJEMEN)
        context["countdown_events"] = CountdownEvent.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        instance = self.get_youtube_instance()
        form = YouTubeSectionForm(request.POST, instance=instance)
        if form.is_valid():
            section = form.save(commit=False)
            section.is_active = True
            apply_audit_fields(section, request.user)
            section.save()
            messages.success(request, "YouTube section berhasil diperbarui.")
            return redirect("dashboard:academic")
        messages.error(request, "Periksa kembali form YouTube section.")
        return self.render_to_response(self.get_context_data(youtube_form=form))


class QuickDownloadCreateView(DashboardObjectFormMixin, CreateView):
    model = QuickDownloadItem
    form_class = QuickDownloadForm
    page_title = "Tambah Quick Download"
    page_description = "Tambah item quick download baru."
    sidebar_section = "academic"
    cancel_url = reverse_lazy("dashboard:academic")
    success_url = reverse_lazy("dashboard:academic")
    success_message = "Quick download berhasil ditambahkan."

    def get_breadcrumbs(self):
        return [("Akademik", reverse("dashboard:academic")), ("Tambah Quick Download", None)]


class QuickDownloadUpdateView(DashboardObjectFormMixin, UpdateView):
    model = QuickDownloadItem
    form_class = QuickDownloadForm
    page_title = "Edit Quick Download"
    page_description = "Perbarui item quick download."
    sidebar_section = "academic"
    cancel_url = reverse_lazy("dashboard:academic")
    success_url = reverse_lazy("dashboard:academic")
    success_message = "Quick download berhasil diperbarui."

    def get_breadcrumbs(self):
        return [("Akademik", reverse("dashboard:academic")), ("Edit Quick Download", None)]


class QuickDownloadDeleteView(DashboardDeleteView):
    model = QuickDownloadItem
    page_title = "Hapus Quick Download"
    page_description = "Item quick download akan dihapus permanen."
    sidebar_section = "academic"
    cancel_url = reverse_lazy("dashboard:academic")
    success_url = reverse_lazy("dashboard:academic")
    success_message = "Quick download berhasil dihapus."

    def get_breadcrumbs(self):
        return [("Akademik", reverse("dashboard:academic")), ("Hapus Quick Download", None)]


class RepositoryMaterialCreateView(DashboardObjectFormMixin, CreateView):
    model = RepositoryMaterial
    form_class = RepositoryMaterialForm
    page_title = "Tambah Repo Bahan Kuliah"
    page_description = "Tambah item baru ke section Akuntansi atau Manajemen."
    sidebar_section = "academic"
    cancel_url = reverse_lazy("dashboard:academic")
    success_url = reverse_lazy("dashboard:academic")
    success_message = "Item repository berhasil ditambahkan."

    def get_breadcrumbs(self):
        return [("Akademik", reverse("dashboard:academic")), ("Tambah Repository", None)]


class RepositoryMaterialUpdateView(DashboardObjectFormMixin, UpdateView):
    model = RepositoryMaterial
    form_class = RepositoryMaterialForm
    page_title = "Edit Repo Bahan Kuliah"
    page_description = "Perbarui item repository bahan kuliah."
    sidebar_section = "academic"
    cancel_url = reverse_lazy("dashboard:academic")
    success_url = reverse_lazy("dashboard:academic")
    success_message = "Item repository berhasil diperbarui."

    def get_breadcrumbs(self):
        return [("Akademik", reverse("dashboard:academic")), ("Edit Repository", None)]


class RepositoryMaterialDeleteView(DashboardDeleteView):
    model = RepositoryMaterial
    page_title = "Hapus Repo Bahan Kuliah"
    page_description = "Item repository akan dihapus permanen."
    sidebar_section = "academic"
    cancel_url = reverse_lazy("dashboard:academic")
    success_url = reverse_lazy("dashboard:academic")
    success_message = "Item repository berhasil dihapus."

    def get_breadcrumbs(self):
        return [("Akademik", reverse("dashboard:academic")), ("Hapus Repository", None)]


class CountdownEventCreateView(DashboardObjectFormMixin, CreateView):
    model = CountdownEvent
    form_class = CountdownEventForm
    page_title = "Tambah Event Countdown"
    page_description = "Tambah event countdown baru."
    sidebar_section = "academic"
    cancel_url = reverse_lazy("dashboard:academic")
    success_url = reverse_lazy("dashboard:academic")
    success_message = "Event countdown berhasil ditambahkan."

    def get_breadcrumbs(self):
        return [("Akademik", reverse("dashboard:academic")), ("Tambah Countdown", None)]


class CountdownEventUpdateView(DashboardObjectFormMixin, UpdateView):
    model = CountdownEvent
    form_class = CountdownEventForm
    page_title = "Edit Event Countdown"
    page_description = "Perbarui event countdown."
    sidebar_section = "academic"
    cancel_url = reverse_lazy("dashboard:academic")
    success_url = reverse_lazy("dashboard:academic")
    success_message = "Event countdown berhasil diperbarui."

    def get_breadcrumbs(self):
        return [("Akademik", reverse("dashboard:academic")), ("Edit Countdown", None)]


class CountdownEventDeleteView(DashboardDeleteView):
    model = CountdownEvent
    page_title = "Hapus Event Countdown"
    page_description = "Event countdown akan dihapus permanen."
    sidebar_section = "academic"
    cancel_url = reverse_lazy("dashboard:academic")
    success_url = reverse_lazy("dashboard:academic")
    success_message = "Event countdown berhasil dihapus."

    def get_breadcrumbs(self):
        return [("Akademik", reverse("dashboard:academic")), ("Hapus Countdown", None)]


class CompetencyPageView(DashboardPageMixin, ListView):
    template_name = "dashboard/competency_page.html"
    model = AgendaCard
    context_object_name = "agenda_cards"
    paginate_by = 15
    page_title = "Kompetensi"
    page_description = "Kelola agenda cards kompetensi dan status publish-nya."
    sidebar_section = "competency-career"
    sidebar_subsection = "competency"

    def get_breadcrumbs(self):
        return [("Kompetensi & Karir", None), ("Kompetensi", None)]


class AgendaCardCreateView(DashboardObjectFormMixin, CreateView):
    model = AgendaCard
    form_class = AgendaCardForm
    page_title = "Tambah Agenda Kompetensi"
    page_description = "Tambah agenda card baru untuk section kompetensi."
    sidebar_section = "competency-career"
    sidebar_subsection = "competency"
    cancel_url = reverse_lazy("dashboard:competency")
    success_url = reverse_lazy("dashboard:competency")
    success_message = "Agenda kompetensi berhasil ditambahkan."

    def get_breadcrumbs(self):
        return [("Kompetensi & Karir", None), ("Kompetensi", reverse("dashboard:competency")), ("Tambah Agenda", None)]


class AgendaCardUpdateView(DashboardObjectFormMixin, UpdateView):
    model = AgendaCard
    form_class = AgendaCardForm
    page_title = "Edit Agenda Kompetensi"
    page_description = "Perbarui agenda card kompetensi."
    sidebar_section = "competency-career"
    sidebar_subsection = "competency"
    cancel_url = reverse_lazy("dashboard:competency")
    success_url = reverse_lazy("dashboard:competency")
    success_message = "Agenda kompetensi berhasil diperbarui."

    def get_breadcrumbs(self):
        return [("Kompetensi & Karir", None), ("Kompetensi", reverse("dashboard:competency")), ("Edit Agenda", None)]


class AgendaCardDeleteView(DashboardDeleteView):
    model = AgendaCard
    page_title = "Hapus Agenda Kompetensi"
    page_description = "Agenda card akan dihapus permanen."
    sidebar_section = "competency-career"
    sidebar_subsection = "competency"
    cancel_url = reverse_lazy("dashboard:competency")
    success_url = reverse_lazy("dashboard:competency")
    success_message = "Agenda kompetensi berhasil dihapus."

    def get_breadcrumbs(self):
        return [("Kompetensi & Karir", None), ("Kompetensi", reverse("dashboard:competency")), ("Hapus Agenda", None)]


class CareerSettingsView(DashboardPageMixin, TemplateView):
    template_name = "dashboard/career_page.html"
    page_title = "Karir"
    page_description = "Kelola resource links tetap untuk section karir."
    sidebar_section = "competency-career"
    sidebar_subsection = "career"

    def get_breadcrumbs(self):
        return [("Kompetensi & Karir", None), ("Karir", None)]

    def get_instance(self):
        return get_singleton_instance(CareerResourceConfiguration, defaults={"is_active": True})

    def get_form(self):
        return CareerResourceConfigurationForm(instance=self.get_instance())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("form", self.get_form())
        return context

    def post(self, request, *args, **kwargs):
        instance = self.get_instance()
        form = CareerResourceConfigurationForm(request.POST, instance=instance)
        if form.is_valid():
            configuration = form.save(commit=False)
            configuration.is_active = True
            apply_audit_fields(configuration, request.user)
            configuration.save()
            messages.success(request, "Resource karir berhasil diperbarui.")
            return redirect("dashboard:career")
        messages.error(request, "Periksa kembali form resource karir.")
        return self.render_to_response(self.get_context_data(form=form))


class AspirationListView(DashboardPageMixin, ListView):
    template_name = "dashboard/aspiration_list.html"
    model = AspirationSubmission
    context_object_name = "aspirations"
    paginate_by = 20
    page_title = "Aspirasi"
    page_description = "Moderasi aspirasi masuk, atur visibility, status, dan featured homepage."
    sidebar_section = "advocacy"
    sidebar_subsection = "aspirations"

    def get_breadcrumbs(self):
        return [("Advokasi", None), ("Aspirasi", None)]

    def get_queryset(self):
        queryset = AspirationSubmission.objects.all()
        q = self.request.GET.get("q")
        status_value = self.request.GET.get("status")
        visibility = self.request.GET.get("visibility")
        featured = self.request.GET.get("featured")

        if q:
            queryset = queryset.filter(
                Q(ticket_id__icontains=q)
                | Q(full_name__icontains=q)
                | Q(email__icontains=q)
                | Q(title__icontains=q)
            )
        if status_value:
            queryset = queryset.filter(status=status_value)
        if visibility:
            queryset = queryset.filter(visibility=visibility)
        if featured in {"true", "false"}:
            queryset = queryset.filter(is_featured=(featured == "true"))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filters"] = {
            "q": self.request.GET.get("q", ""),
            "status": self.request.GET.get("status", ""),
            "visibility": self.request.GET.get("visibility", ""),
            "featured": self.request.GET.get("featured", ""),
        }
        context["featured_count"] = AspirationSubmission.objects.filter(is_featured=True).count()
        context["pagination_query"] = build_pagination_querystring(self.request)
        return context


class AspirationDetailView(DashboardPageMixin, TemplateView):
    template_name = "dashboard/aspiration_detail.html"
    page_title = "Detail Aspirasi"
    page_description = "Lihat detail tiket, attachment, dan perbarui status moderasi."
    sidebar_section = "advocacy"
    sidebar_subsection = "aspirations"

    def get_breadcrumbs(self):
        return [("Advokasi", None), ("Aspirasi", reverse("dashboard:aspiration-list")), ("Detail", None)]

    def get_object(self):
        return get_object_or_404(AspirationSubmission, pk=self.kwargs["pk"])

    def get_form(self):
        return AspirationUpdateForm(instance=self.get_object())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        aspiration = self.get_object()
        context["aspiration"] = aspiration
        context.setdefault("form", self.get_form())
        context["activity_logs"] = aspiration.activity_logs.all()[:10]
        return context

    def post(self, request, *args, **kwargs):
        aspiration = self.get_object()
        form = AspirationUpdateForm(request.POST, instance=aspiration)
        if form.is_valid():
            update_aspiration_submission(aspiration, form.cleaned_data, request.user)
            messages.success(request, "Aspirasi berhasil diperbarui.")
            return redirect("dashboard:aspiration-detail", pk=aspiration.pk)
        messages.error(request, "Periksa kembali form pembaruan aspirasi.")
        return self.render_to_response(self.get_context_data(form=form))


class AspirationFeatureToggleView(PostActionMessageMixin, View):
    success_message = "Featured aspirasi berhasil diperbarui."

    def handle_action(self, request, *args, **kwargs):
        aspiration = get_object_or_404(AspirationSubmission, pk=kwargs["pk"])
        should_feature = kwargs["feature_action"] == "set"
        aspiration.updated_by = request.user
        try:
            set_featured_state(aspiration, is_featured=should_feature)
            if not should_feature:
                self.success_message = "Aspirasi berhasil dihapus dari featured."
        except ValidationError as exc:
            messages.error(request, "; ".join(exc.messages))
        return redirect(request.POST.get("next") or reverse("dashboard:aspiration-list"))


class AspirationDeleteView(DashboardDeleteView):
    model = AspirationSubmission
    page_title = "Hapus Aspirasi"
    page_description = "Aspirasi dan log terkait akan dihapus permanen."
    sidebar_section = "advocacy"
    sidebar_subsection = "aspirations"
    cancel_url = reverse_lazy("dashboard:aspiration-list")
    success_url = reverse_lazy("dashboard:aspiration-list")
    success_message = "Aspirasi berhasil dihapus."

    def get_breadcrumbs(self):
        return [("Advokasi", None), ("Aspirasi", reverse("dashboard:aspiration-list")), ("Hapus", None)]


class TicketTrackingAdminView(DashboardPageMixin, TemplateView):
    template_name = "dashboard/ticket_tracking.html"
    page_title = "Lacak Tiket"
    page_description = "Cari tiket berdasarkan ticket ID, nama, email, atau judul lalu buka detailnya."
    sidebar_section = "advocacy"
    sidebar_subsection = "tickets"

    def get_breadcrumbs(self):
        return [("Advokasi", None), ("Lacak Tiket", None)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = TicketSearchForm(self.request.GET or None)
        queryset = AspirationSubmission.objects.all()

        query = ""
        if form.is_valid():
            query = form.cleaned_data.get("q", "")
            if query:
                queryset = queryset.filter(
                    Q(ticket_id__icontains=query)
                    | Q(full_name__icontains=query)
                    | Q(email__icontains=query)
                    | Q(title__icontains=query)
                )

        paginator = Paginator(queryset, 20)
        page_obj = paginator.get_page(self.request.GET.get("page"))

        context["search_form"] = form
        context["query"] = query
        context["page_obj"] = page_obj
        context["tickets"] = page_obj.object_list
        context["paginator"] = paginator
        context["pagination_query"] = build_pagination_querystring(self.request)
        return context
