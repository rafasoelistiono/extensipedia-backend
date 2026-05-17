from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from analytics_dashboard.models import ActivityEvent, ActivityEventCounter, VisitorDailyVisit
from analytics_dashboard.services import build_dashboard_summary
from aspirations.models import AspirationSubmission


def unwrap_response_data(response):
    if isinstance(response.data, dict) and "data" in response.data:
        return response.data["data"]
    return response.data


class PublicActivityEventTests(APITestCase):
    url = reverse("public-activity-events")

    def build_payload(self, **overrides):
        payload = {
            "action_key": "home.features.academic.access_now",
            "label": "Akses Sekarang",
            "page_path": "/",
            "target_type": "internal_link",
            "target_id": None,
            "target_url": "/akademik",
            "metadata": {
                "section": "features",
                "source": "homepage",
            },
        }
        payload.update(overrides)
        return payload

    def test_public_activity_event_records_click_and_returns_total_count(self):
        response = self.client.post(
            self.url,
            data=self.build_payload(),
            format="json",
            HTTP_X_FORWARDED_FOR="203.0.113.10",
            HTTP_USER_AGENT="Extensipedia Test Browser",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = unwrap_response_data(response)
        self.assertEqual(payload["action_key"], "home.features.academic.access_now")
        self.assertEqual(payload["total_count"], 1)

        counter = ActivityEventCounter.objects.get(action_key="home.features.academic.access_now")
        event = ActivityEvent.objects.get(action_key="home.features.academic.access_now")
        self.assertEqual(counter.total_count, 1)
        self.assertEqual(event.label, "Akses Sekarang")
        self.assertEqual(event.page_path, "/")
        self.assertEqual(event.target_url, "/akademik")
        self.assertEqual(event.metadata["source"], "homepage")
        self.assertTrue(event.session_key)
        self.assertTrue(event.ip_hash)
        self.assertNotEqual(event.ip_hash, "203.0.113.10")
        self.assertEqual(event.user_agent, "Extensipedia Test Browser")

    def test_activity_event_without_idempotency_counts_each_click(self):
        first_response = self.client.post(self.url, data=self.build_payload(), format="json")
        second_response = self.client.post(self.url, data=self.build_payload(), format="json")

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(unwrap_response_data(second_response)["total_count"], 2)
        self.assertEqual(ActivityEvent.objects.count(), 2)
        self.assertEqual(ActivityEventCounter.objects.get().total_count, 2)

    def test_activity_event_idempotency_key_prevents_double_count(self):
        payload = self.build_payload(idempotency_key="homepage-click-1")

        first_response = self.client.post(self.url, data=payload, format="json")
        second_response = self.client.post(self.url, data=payload, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(unwrap_response_data(first_response)["total_count"], 1)
        self.assertEqual(unwrap_response_data(second_response)["total_count"], 1)
        self.assertEqual(ActivityEvent.objects.count(), 1)
        self.assertEqual(ActivityEventCounter.objects.get().total_count, 1)

    def test_activity_event_rejects_unknown_action_key(self):
        response = self.client.post(
            self.url,
            data=self.build_payload(action_key="home.unknown.action"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ActivityEvent.objects.count(), 0)

    def test_aspiration_activity_click_tracking_does_not_update_public_vote_counts(self):
        aspiration = AspirationSubmission.objects.create(
            ticket_id="ASP-ACT000001",
            full_name="Tracker User",
            npm="22000005",
            email="tracker@example.com",
            title="Tracked aspiration",
            short_description="Tracked aspiration description",
        )

        response = self.client.post(
            self.url,
            data=self.build_payload(
                action_key="home.aspiration.upvote",
                label="Like",
                target_type="aspiration",
                target_id=str(aspiration.pk),
                target_url=None,
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        aspiration.refresh_from_db()
        self.assertEqual(aspiration.upvote_count, 0)
        self.assertEqual(ActivityEvent.objects.get().target_id, str(aspiration.pk))

    def test_dashboard_summary_counts_activity_events_all_time_from_new_tracking_only(self):
        VisitorDailyVisit.objects.create(
            visit_date=timezone.localdate(),
            fingerprint_hash="legacy-visitor-record",
            first_path="/api/v1/public/about/hero/",
            last_seen_at=timezone.now(),
        )

        empty_summary = build_dashboard_summary()
        self.assertEqual(empty_summary["cards"]["total_activity_events_all_time"], 0)

        self.client.post(self.url, data=self.build_payload(action_key="home.hero.access_academic"), format="json")
        self.client.post(self.url, data=self.build_payload(action_key="home.ticket.view_form"), format="json")

        summary = build_dashboard_summary()
        self.assertEqual(summary["cards"]["total_activity_events_all_time"], 2)
        self.assertNotIn("total_visitors_last_30_days", summary["cards"])
