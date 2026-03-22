from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from about.models import CabinetCalendar
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
