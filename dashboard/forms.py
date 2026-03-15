from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from about.models import AboutSection, CabinetCalendar
from academic.models import CountdownEvent, QuickDownloadItem, RepositoryMaterial, YouTubeSection
from aspirations.models import AspirationSubmission
from career.models import CareerResourceConfiguration
from competency.models import AgendaCard


class BootstrapFormMixin:
    def _apply_bootstrap_classes(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "form-check-input"
            elif isinstance(widget, forms.RadioSelect):
                widget.attrs["class"] = "form-check-input"
            elif isinstance(widget, forms.FileInput):
                widget.attrs["class"] = "form-control"
            else:
                widget.attrs["class"] = "form-control"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap_classes()


class DashboardLoginForm(BootstrapFormMixin, forms.Form):
    username = forms.CharField(label="Username", max_length=150)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    error_messages = {
        "invalid_login": "Username atau password tidak valid.",
        "no_access": "Akun ini tidak memiliki akses ke dashboard admin.",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(self.error_messages["invalid_login"])
            if not self.user_cache.is_superuser:
                raise forms.ValidationError(self.error_messages["no_access"])
        return cleaned_data

    def get_user(self):
        return self.user_cache


class DashboardModelForm(BootstrapFormMixin, forms.ModelForm):
    pass


class AboutSectionForm(DashboardModelForm):
    class Meta:
        model = AboutSection
        fields = ("title", "subtitle", "description", "image")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }


class CabinetCalendarForm(DashboardModelForm):
    class Meta:
        model = CabinetCalendar
        fields = ("title", "description", "embed_url", "embed_code", "display_order", "is_active")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "embed_code": forms.Textarea(attrs={"rows": 4}),
        }


class QuickDownloadForm(DashboardModelForm):
    source_type = forms.ChoiceField(
        label="Tipe Sumber",
        choices=(("file", "File upload"), ("link", "External link")),
        widget=forms.RadioSelect,
    )

    class Meta:
        model = QuickDownloadItem
        fields = ("title", "source_type", "file", "external_url", "display_order", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["source_type"].initial = "file" if self.instance.file else "link"
        else:
            self.fields["source_type"].initial = "file"

    def clean(self):
        cleaned_data = super().clean()
        source_type = cleaned_data.get("source_type")
        file = cleaned_data.get("file")
        external_url = cleaned_data.get("external_url")

        if source_type == "file":
            external_url = ""
            if not file and not getattr(self.instance, "file", None):
                self.add_error("file", "Upload a file for this quick download item.")
        elif source_type == "link":
            if not external_url:
                self.add_error("external_url", "Provide a URL for this quick download item.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data["source_type"] == "file":
            instance.external_url = ""
        else:
            instance.file = self.cleaned_data.get("file") or None
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class RepositoryMaterialForm(DashboardModelForm):
    class Meta:
        model = RepositoryMaterial
        fields = ("section", "title", "google_drive_link", "display_order")


class YouTubeSectionForm(DashboardModelForm):
    class Meta:
        model = YouTubeSection
        fields = ("title", "description", "embed_url", "embed_code")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "embed_code": forms.Textarea(attrs={"rows": 4}),
        }


class CountdownEventForm(DashboardModelForm):
    class Meta:
        model = CountdownEvent
        fields = ("title", "target_datetime", "display_order", "is_active")
        widgets = {
            "target_datetime": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={"type": "datetime-local"},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["target_datetime"].input_formats = ("%Y-%m-%dT%H:%M",)


class AgendaCardForm(DashboardModelForm):
    class Meta:
        model = AgendaCard
        fields = (
            "title",
            "short_description",
            "urgency_tag",
            "recommendation_tag",
            "category_tag",
            "scope_tag",
            "pricing_tag",
            "deadline_date",
            "registration_link",
            "google_calendar_link",
            "is_active",
            "sort_order",
        )
        widgets = {
            "short_description": forms.Textarea(attrs={"rows": 3}),
            "deadline_date": forms.DateInput(attrs={"type": "date"}),
        }


class CareerResourceConfigurationForm(DashboardModelForm):
    class Meta:
        model = CareerResourceConfiguration
        fields = (
            "cv_templates",
            "cover_letter",
            "portfolio_guide",
            "salary_script",
            "case_study_interview_prep",
        )


class AspirationUpdateForm(DashboardModelForm):
    class Meta:
        model = AspirationSubmission
        fields = ("status", "visibility", "is_featured")

    def clean(self):
        cleaned_data = super().clean()
        instance = self.instance
        instance.status = cleaned_data.get("status", instance.status)
        instance.visibility = cleaned_data.get("visibility", instance.visibility)
        instance.is_featured = cleaned_data.get("is_featured", instance.is_featured)
        try:
            instance.clean()
        except ValidationError as exc:
            raise forms.ValidationError(exc.message_dict or exc.messages)
        return cleaned_data


class TicketSearchForm(BootstrapFormMixin, forms.Form):
    q = forms.CharField(required=False, label="Cari tiket", max_length=255)
