from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from academic.models import AcademicDigitalResourceConfiguration
from advocacy.models import AdvocacyPolicyResourceConfiguration
from accounts.models import User
from competency.constants import DEFAULT_LOMBA_CARI_TIM_LINK
from competency.models import AgendaCard, CompetencyWinnerSlide
from dashboard.services import LOCAL_DASHBOARD_PASSWORD, ensure_local_development_dashboard_users


class DashboardAccessTests(TestCase):
    password = "extensipedia.feb.ui"

    def create_dashboard_user(self, *, username, scope):
        return User.objects.create_user(
            email=f"{username}@example.com",
            dashboard_username=username,
            full_name=username.title(),
            password=self.password,
            is_staff=True,
            dashboard_access_scope=scope,
        )

    def test_academic_user_only_accesses_allowed_sections(self):
        self.create_dashboard_user(username="akademik", scope=User.DashboardAccessScopes.ACADEMIC)

        response = self.client.post(
            reverse("dashboard:login"),
            {"username": "akademik", "password": self.password},
        )

        self.assertRedirects(response, reverse("dashboard:home"))
        self.assertEqual(self.client.get(reverse("dashboard:home")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard:about")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard:academic")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard:profile")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard:competency")).status_code, 403)
        self.assertEqual(self.client.get(reverse("dashboard:career")).status_code, 403)
        self.assertEqual(self.client.get(reverse("dashboard:aspiration-list")).status_code, 403)
        self.assertEqual(self.client.get(reverse("dashboard:ticket-tracking")).status_code, 403)
        self.assertEqual(self.client.get(reverse("dashboard:advocacy-resources")).status_code, 403)

    def test_competency_user_accesses_competency_and_career_sections(self):
        competency_user = self.create_dashboard_user(
            username="kompetensi",
            scope=User.DashboardAccessScopes.COMPETENCY,
        )
        self.client.force_login(competency_user)

        self.assertEqual(self.client.get(reverse("dashboard:home")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard:about")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard:competency")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard:career")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard:profile")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard:academic")).status_code, 403)
        self.assertEqual(self.client.get(reverse("dashboard:aspiration-list")).status_code, 403)
        self.assertEqual(self.client.get(reverse("dashboard:advocacy-resources")).status_code, 403)

    def test_lomba_agenda_uses_default_cari_tim_link_when_team_finding_link_is_empty(self):
        competency_user = self.create_dashboard_user(
            username="kompetensi",
            scope=User.DashboardAccessScopes.COMPETENCY,
        )
        self.client.force_login(competency_user)

        response = self.client.post(
            reverse("dashboard:agenda-card-create"),
            {
                "title": "Business Case Competition",
                "short_description": "Kompetisi studi kasus untuk mahasiswa.",
                "urgency_tag": "True",
                "recommendation_tag": "True",
                "category_tag": AgendaCard.CategoryTag.LOMBA,
                "scope_tag": AgendaCard.ScopeTag.NASIONAL,
                "pricing_tag": AgendaCard.PricingTag.TIDAK_BERBAYAR,
                "deadline_date": "2026-05-20",
                "registration_link": "https://example.com/registration",
                "team_finding_link": "",
                "google_calendar_link": "",
                "is_active": "on",
            },
        )

        self.assertRedirects(response, reverse("dashboard:competency"))
        agenda = AgendaCard.objects.get(title="Business Case Competition")
        self.assertEqual(agenda.registration_link, "https://example.com/registration")
        self.assertEqual(agenda.team_finding_link, DEFAULT_LOMBA_CARI_TIM_LINK)

    def test_agenda_create_page_renders_lomba_default_link_automation(self):
        competency_user = self.create_dashboard_user(
            username="kompetensi",
            scope=User.DashboardAccessScopes.COMPETENCY,
        )
        self.client.force_login(competency_user)

        response = self.client.get(reverse("dashboard:agenda-card-create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, DEFAULT_LOMBA_CARI_TIM_LINK)
        self.assertContains(response, "Link Cari Tim")
        self.assertContains(response, "Link Pendaftaran")

    def test_academic_user_can_update_digital_resource_links(self):
        user = self.create_dashboard_user(username="akademik", scope=User.DashboardAccessScopes.ACADEMIC)
        self.client.force_login(user)

        response = self.client.post(
            reverse("dashboard:academic"),
            {
                "form_type": "digital_resources",
                "canva_pro_ekstensi": "https://example.com/canva-pro-ekstensi",
                "gemini_advanced": "https://example.com/gemini-advanced",
            },
        )

        self.assertRedirects(response, reverse("dashboard:academic"))
        configuration = AcademicDigitalResourceConfiguration.objects.get()
        self.assertEqual(configuration.canva_pro_ekstensi, "https://example.com/canva-pro-ekstensi")
        self.assertEqual(configuration.gemini_advanced, "https://example.com/gemini-advanced")

    def test_advocacy_user_can_update_policy_resource_links(self):
        user = self.create_dashboard_user(username="advokasi", scope=User.DashboardAccessScopes.ADVOCACY)
        self.client.force_login(user)

        self.assertEqual(self.client.get(reverse("dashboard:advocacy-resources")).status_code, 200)
        response = self.client.post(
            reverse("dashboard:advocacy-resources"),
            {
                "siak_war": "https://example.com/siak-war",
                "cicilan_ukt": "https://example.com/cicilan-ukt",
                "alur_skpi": "https://example.com/alur-skpi",
            },
        )

        self.assertRedirects(response, reverse("dashboard:advocacy-resources"))
        configuration = AdvocacyPolicyResourceConfiguration.objects.get()
        self.assertEqual(configuration.siak_war, "https://example.com/siak-war")
        self.assertEqual(configuration.cicilan_ukt, "https://example.com/cicilan-ukt")
        self.assertEqual(configuration.alur_skpi, "https://example.com/alur-skpi")

    def test_public_resource_link_endpoints_return_active_configurations(self):
        AcademicDigitalResourceConfiguration.objects.create(
            canva_pro_ekstensi="https://example.com/canva-pro-ekstensi",
            gemini_advanced="https://example.com/gemini-advanced",
        )
        AdvocacyPolicyResourceConfiguration.objects.create(
            siak_war="https://example.com/siak-war",
            cicilan_ukt="https://example.com/cicilan-ukt",
            alur_skpi="https://example.com/alur-skpi",
        )

        academic_response = self.client.get("/api/v1/public/academic/digital-resources/")
        advocacy_response = self.client.get("/api/v1/public/advocacy/policy-resources/")

        self.assertEqual(academic_response.status_code, 200)
        self.assertEqual(advocacy_response.status_code, 200)
        self.assertEqual(academic_response.json()["data"]["canva_pro_ekstensi"], "https://example.com/canva-pro-ekstensi")
        self.assertEqual(advocacy_response.json()["data"]["siak_war"], "https://example.com/siak-war")

    def test_profile_can_update_dashboard_username_and_password(self):
        user = self.create_dashboard_user(username="advokasi", scope=User.DashboardAccessScopes.ADVOCACY)
        self.client.force_login(user)

        response = self.client.post(
            reverse("dashboard:profile"),
            {
                "username": "advokasi-baru",
                "new_password1": "passwordbaru123",
                "new_password2": "passwordbaru123",
            },
        )

        self.assertRedirects(response, reverse("dashboard:profile"))
        user.refresh_from_db()
        self.assertEqual(user.dashboard_username, "advokasi-baru")
        self.assertTrue(user.check_password("passwordbaru123"))

        self.client.logout()
        relogin_response = self.client.post(
            reverse("dashboard:login"),
            {"username": "advokasi-baru", "password": "passwordbaru123"},
        )
        self.assertRedirects(relogin_response, reverse("dashboard:home"))

    @override_settings(DEBUG=True)
    def test_local_dashboard_bootstrap_creates_four_default_accounts(self):
        users = ensure_local_development_dashboard_users()

        self.assertEqual(set(users), {"superadmin", "akademik", "kompetensi", "advokasi"})
        self.assertTrue(users["superadmin"].is_superuser)
        self.assertEqual(users["akademik"].dashboard_access_scope, User.DashboardAccessScopes.ACADEMIC)
        self.assertEqual(users["kompetensi"].dashboard_access_scope, User.DashboardAccessScopes.COMPETENCY)
        self.assertEqual(users["advokasi"].dashboard_access_scope, User.DashboardAccessScopes.ADVOCACY)
        self.assertIn("career", users["kompetensi"].dashboard_allowed_sections)
        self.assertTrue(users["kompetensi"].check_password(LOCAL_DASHBOARD_PASSWORD))

    @override_settings(DEBUG=True)
    def test_local_dashboard_bootstrap_deactivates_legacy_career_account(self):
        legacy_career_user = User.objects.create_user(
            email="karir@extensipedia.local",
            dashboard_username="karir",
            full_name="Admin Karir",
            password=LOCAL_DASHBOARD_PASSWORD,
            is_staff=True,
            dashboard_access_scope="career",
        )

        users = ensure_local_development_dashboard_users()

        self.assertNotIn("karir", users)
        legacy_career_user.refresh_from_db()
        self.assertFalse(legacy_career_user.is_active)
        self.assertFalse(legacy_career_user.is_staff)
        self.assertFalse(legacy_career_user.is_superuser)
        self.assertEqual(legacy_career_user.dashboard_access_scope, User.DashboardAccessScopes.COMPETENCY)

    @override_settings(DEBUG=True)
    def test_local_dashboard_bootstrap_does_not_reset_profile_credentials(self):
        users = ensure_local_development_dashboard_users()
        competency_user = users["kompetensi"]
        competency_user.dashboard_username = "kompetensi-baru"
        competency_user.set_password("passwordbaru123")
        competency_user.save(update_fields=["dashboard_username", "password"])

        ensure_local_development_dashboard_users()

        competency_user.refresh_from_db()
        self.assertEqual(competency_user.dashboard_username, "kompetensi-baru")
        self.assertTrue(competency_user.check_password("passwordbaru123"))


def build_test_image(name="winner-slide.png"):
    buffer = BytesIO()
    Image.new("RGB", (2, 2), color=(12, 34, 56)).save(buffer, format="PNG")
    return SimpleUploadedFile(
        name,
        buffer.getvalue(),
        content_type="image/png",
    )


class DashboardWinnerSlideTests(TestCase):
    password = "extensipedia.feb.ui"

    def create_dashboard_user(self, *, username, scope):
        return User.objects.create_user(
            email=f"{username}@example.com",
            dashboard_username=username,
            full_name=username.title(),
            password=self.password,
            is_staff=True,
            dashboard_access_scope=scope,
        )

    def setUp(self):
        self.user = self.create_dashboard_user(
            username="kompetensi",
            scope=User.DashboardAccessScopes.COMPETENCY,
        )
        self.client.force_login(self.user)

    def test_competency_page_renders_fixed_winner_slide_slots_when_table_is_empty(self):
        CompetencyWinnerSlide.objects.all().delete()

        response = self.client.get(reverse("dashboard:competency"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CompetencyWinnerSlide.objects.count(), 0)
        self.assertEqual(
            [slot["number"] for slot in response.context["winner_slide_slots"]],
            [1, 2, 3, 4, 5],
        )
        self.assertTrue(all(slot["item"].pk is None for slot in response.context["winner_slide_slots"]))

    def test_winner_slide_slot_form_can_create_missing_slot_record(self):
        CompetencyWinnerSlide.objects.all().delete()

        response = self.client.post(
            reverse("dashboard:winner-slide-update", args=[3]),
            {
                "alt_text": "Juara tingkat nasional",
                "image": build_test_image(),
            },
        )

        self.assertRedirects(response, reverse("dashboard:competency"))
        winner_slide = CompetencyWinnerSlide.objects.get(display_order=3)
        self.assertEqual(winner_slide.alt_text, "Juara tingkat nasional")
        self.assertTrue(bool(winner_slide.image))
