from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from accounts.models import User
from competency.models import CompetencyWinnerSlide
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

    def test_competency_and_career_users_access_separate_sections(self):
        competency_user = self.create_dashboard_user(
            username="kompetensi",
            scope=User.DashboardAccessScopes.COMPETENCY,
        )
        self.client.force_login(competency_user)

        self.assertEqual(self.client.get(reverse("dashboard:competency")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard:career")).status_code, 403)

        self.client.logout()
        career_user = self.create_dashboard_user(username="karir", scope=User.DashboardAccessScopes.CAREER)
        self.client.force_login(career_user)

        self.assertEqual(self.client.get(reverse("dashboard:home")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard:about")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard:career")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard:profile")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dashboard:competency")).status_code, 403)
        self.assertEqual(self.client.get(reverse("dashboard:academic")).status_code, 403)
        self.assertEqual(self.client.get(reverse("dashboard:aspiration-list")).status_code, 403)

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
    def test_local_dashboard_bootstrap_creates_five_default_accounts(self):
        users = ensure_local_development_dashboard_users()

        self.assertEqual(set(users), {"superadmin", "akademik", "kompetensi", "karir", "advokasi"})
        self.assertTrue(users["superadmin"].is_superuser)
        self.assertEqual(users["akademik"].dashboard_access_scope, User.DashboardAccessScopes.ACADEMIC)
        self.assertEqual(users["kompetensi"].dashboard_access_scope, User.DashboardAccessScopes.COMPETENCY)
        self.assertEqual(users["karir"].dashboard_access_scope, User.DashboardAccessScopes.CAREER)
        self.assertEqual(users["advokasi"].dashboard_access_scope, User.DashboardAccessScopes.ADVOCACY)
        self.assertTrue(users["karir"].check_password(LOCAL_DASHBOARD_PASSWORD))

    @override_settings(DEBUG=True)
    def test_local_dashboard_bootstrap_does_not_reset_profile_credentials(self):
        users = ensure_local_development_dashboard_users()
        career_user = users["karir"]
        career_user.dashboard_username = "karir-baru"
        career_user.set_password("passwordbaru123")
        career_user.save(update_fields=["dashboard_username", "password"])

        ensure_local_development_dashboard_users()

        career_user.refresh_from_db()
        self.assertEqual(career_user.dashboard_username, "karir-baru")
        self.assertTrue(career_user.check_password("passwordbaru123"))


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
