import base64

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from competency.models import CompetencyWinnerSlide


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


def build_test_image(name="winner-slide.png"):
    return SimpleUploadedFile(
        name,
        base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9p6k9TQAAAAASUVORK5CYII="
        ),
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
