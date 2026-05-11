from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from about.models import AboutSection, CabinetCalendar
from accounts.models import User


def unwrap_response_data(response):
    if isinstance(response.data, dict) and "data" in response.data:
        return response.data["data"]
    return response.data


class AboutSingletonApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin-about@example.com",
            password="password123",
            full_name="Admin About",
            is_staff=True,
            is_superuser=True,
        )

    def test_admin_cabinet_calendar_endpoint_upserts_singleton(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.put(
            reverse("admin-about:admin-cabinet-calendar"),
            {
                "title": "Kalender Kabinet",
                "description": "Agenda kabinet",
                "embed_url": "https://calendar.google.com/calendar/embed?src=test@example.com",
                "embed_code": "",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CabinetCalendar.objects.count(), 1)
        self.assertEqual(CabinetCalendar.objects.get().title, "Kalender Kabinet")

    def test_admin_about_section_endpoint_upserts_program_detail_links(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse("admin-about:admin-tentang-kami"),
            {
                "title": "Tentang Kami",
                "description": "Deskripsi tentang kami",
                "extensipedia_link": "https://example.com/extensipedia",
                "study_boost_exam_blast_link": "https://example.com/study-boost",
                "fun_enlightenment_link": "https://example.com/fun",
                "career_catalyst_link": "https://example.com/career-catalyst",
                "explore_link": "https://example.com/explore",
                "business_partnership_link": "https://example.com/business",
                "jaring_aspirasi_link": "https://example.com/aspirasi",
                "kajian_strategis_link": "https://example.com/kajian",
                "bincang_sekma_link": "https://example.com/bincang",
                "reach_project_link": "https://example.com/reach",
                "talent_interest_link": "https://example.com/talent",
                "branding_dokumentasi_link": "https://example.com/branding",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(AboutSection.objects.count(), 1)
        about_section = AboutSection.objects.get()
        self.assertEqual(about_section.extensipedia_link, "https://example.com/extensipedia")
        self.assertEqual(about_section.branding_dokumentasi_link, "https://example.com/branding")

    def test_public_about_section_returns_program_detail_link_groups(self):
        AboutSection.objects.create(
            title="Tentang Kami",
            description="Deskripsi tentang kami",
            extensipedia_link="https://example.com/extensipedia",
            study_boost_exam_blast_link="https://example.com/study-boost",
            fun_enlightenment_link="https://example.com/fun",
            career_catalyst_link="https://example.com/career-catalyst",
            explore_link="https://example.com/explore",
            business_partnership_link="https://example.com/business",
            jaring_aspirasi_link="https://example.com/aspirasi",
            kajian_strategis_link="https://example.com/kajian",
            bincang_sekma_link="https://example.com/bincang",
            reach_project_link="https://example.com/reach",
            talent_interest_link="https://example.com/talent",
            branding_dokumentasi_link="https://example.com/branding",
        )

        response = self.client.get(reverse("public-about:public-tentang-kami"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = unwrap_response_data(response)
        self.assertEqual(len(payload["program_detail_links"]), 4)
        self.assertEqual(len(payload["program_detail_links"][0]["links"]), 3)
        self.assertEqual(payload["program_detail_links"][0]["links"][0]["key"], "extensipedia_link")
        self.assertEqual(payload["program_detail_links"][0]["links"][0]["url"], "https://example.com/extensipedia")

    def test_public_cabinet_calendar_endpoint_returns_single_object_without_display_order(self):
        CabinetCalendar.objects.create(
            title="Kalender Kabinet",
            description="Agenda kabinet",
            embed_url="https://calendar.google.com/calendar/embed?src=test@example.com",
            embed_code='<iframe src="https://calendar.google.com/calendar/embed?src=test@example.com"></iframe>',
        )

        response = self.client.get(reverse("public-about:public-cabinet-calendar"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = unwrap_response_data(response)
        self.assertEqual(payload["title"], "Kalender Kabinet")
        self.assertEqual(
            payload["embed_code"],
            '<iframe src="https://calendar.google.com/calendar/embed?src=test@example.com"></iframe>',
        )
        self.assertNotIn("display_order", payload)
