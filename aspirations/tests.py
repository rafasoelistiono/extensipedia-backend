from unittest.mock import patch
from uuid import UUID

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from aspirations.models import AspirationSubmission
from aspirations.services import generate_ticket_id


def unwrap_response_data(response):
    if isinstance(response.data, dict) and "data" in response.data:
        return response.data["data"]
    return response.data


class AspirationPublicFlowTests(APITestCase):
    def test_aspiration_submission_success_and_email_sent(self):
        url = reverse("public-aspirations:aspiration-submit")
        attachment = SimpleUploadedFile("evidence.pdf", b"file-content", content_type="application/pdf")

        response = self.client.post(
            url,
            data={
                "full_name": "Rina Putri",
                "npm": "22123456",
                "email": "rina@example.com",
                "title": "Perbaikan WiFi Gedung A",
                "short_description": "WiFi sering putus saat jam kuliah.",
                "evidence_attachment": attachment,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AspirationSubmission.objects.count(), 1)
        aspiration = AspirationSubmission.objects.get()
        self.assertTrue(aspiration.ticket_id.startswith("ASP-"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(aspiration.ticket_id, mail.outbox[0].body)

    def test_ticket_id_generation_is_unique(self):
        AspirationSubmission.objects.create(
            ticket_id="ASP-AAAAAAAAAA",
            full_name="Existing User",
            npm="22000001",
            email="existing@example.com",
            title="Existing",
            short_description="Existing description",
        )

        collision_uuid = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
        unique_uuid = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")

        with patch("aspirations.services.uuid.uuid4", side_effect=[collision_uuid, unique_uuid]):
            ticket_id = generate_ticket_id()

        self.assertEqual(ticket_id, "ASP-BBBBBBBBBB")

    def test_anonymous_featured_aspiration_hides_sender_name(self):
        AspirationSubmission.objects.create(
            ticket_id="ASP-ANON000001",
            full_name="Hidden User",
            npm="22000002",
            email="hidden@example.com",
            title="Anonymous Ticket",
            short_description="Hidden sender",
            visibility=AspirationSubmission.Visibility.ANONYMOUS,
            status=AspirationSubmission.Status.INVESTIGATING,
            is_featured=True,
        )

        response = self.client.get(reverse("public-aspirations:aspiration-featured"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = unwrap_response_data(response)
        self.assertEqual(payload[0]["sender_name"], None)
        self.assertNotIn("email", payload[0])
        self.assertNotIn("npm", payload[0])

    def test_public_voting_increments_counts(self):
        aspiration = AspirationSubmission.objects.create(
            ticket_id="ASP-VOTE00001",
            full_name="Visible User",
            npm="22000003",
            email="vote@example.com",
            title="Voting Ticket",
            short_description="Voting ticket description",
            visibility=AspirationSubmission.Visibility.PUBLIC,
            status=AspirationSubmission.Status.RESOLVED,
            is_featured=True,
        )

        upvote_url = reverse("public-aspirations:aspiration-upvote", args=[aspiration.pk])
        vote_url = reverse("public-aspirations:aspiration-vote", args=[aspiration.pk])

        self.client.post(upvote_url)
        self.client.post(upvote_url)
        self.client.post(vote_url)
        self.client.post(vote_url)

        aspiration.refresh_from_db()
        self.assertEqual(aspiration.upvote_count, 2)
        self.assertEqual(aspiration.vote_count, 2)

    def test_public_voting_without_trailing_slash_is_supported(self):
        aspiration = AspirationSubmission.objects.create(
            ticket_id="ASP-VOTE00002",
            full_name="Visible User",
            npm="22000013",
            email="vote2@example.com",
            title="Voting Ticket 2",
            short_description="Voting ticket description 2",
            visibility=AspirationSubmission.Visibility.PUBLIC,
            status=AspirationSubmission.Status.SUBMITTED,
            is_featured=False,
        )

        upvote_url = f"/api/v1/public/aspirations/{aspiration.pk}/upvote"
        vote_url = f"/api/v1/public/aspirations/{aspiration.pk}/vote"

        upvote_response = self.client.post(upvote_url)
        vote_response = self.client.post(vote_url)

        self.assertEqual(upvote_response.status_code, status.HTTP_200_OK)
        self.assertEqual(vote_response.status_code, status.HTTP_200_OK)

        aspiration.refresh_from_db()
        self.assertEqual(aspiration.upvote_count, 1)
        self.assertEqual(aspiration.vote_count, 1)
        self.assertEqual(unwrap_response_data(upvote_response)["upvote_count"], 1)
        self.assertEqual(unwrap_response_data(vote_response)["vote_count"], 1)

    def test_ticket_tracking_returns_public_safe_payload(self):
        aspiration = AspirationSubmission.objects.create(
            ticket_id="ASP-ABCDEF1234",
            full_name="Tracker User",
            npm="22000004",
            email="track@example.com",
            title="Tracking Ticket",
            short_description="Track this ticket",
            visibility=AspirationSubmission.Visibility.PUBLIC,
            status=AspirationSubmission.Status.INVESTIGATING,
        )

        response = self.client.get(f"{reverse('public-tickets:ticket-track')}?ticket_id={aspiration.ticket_id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = unwrap_response_data(response)
        self.assertEqual(payload["ticket_id"], aspiration.ticket_id)
        self.assertEqual(payload["title"], aspiration.title)
        self.assertNotIn("email", payload)
        self.assertNotIn("npm", payload)

    def test_featured_aspirations_max_six(self):
        for index in range(6):
            AspirationSubmission.objects.create(
                ticket_id=f"ASP-FEAT0000{index}",
                full_name=f"User {index}",
                npm=f"2200001{index}",
                email=f"user{index}@example.com",
                title=f"Featured {index}",
                short_description="Featured ticket",
                visibility=AspirationSubmission.Visibility.PUBLIC,
                status=AspirationSubmission.Status.INVESTIGATING,
                is_featured=True,
            )

        admin = User.objects.create_user(
            email="admin@example.com",
            password="password123",
            full_name="Admin User",
            is_staff=True,
        )
        extra = AspirationSubmission.objects.create(
            ticket_id="ASP-FEAT99999",
            full_name="User 7",
            npm="22000017",
            email="user7@example.com",
            title="Extra Featured",
            short_description="Extra featured ticket",
            visibility=AspirationSubmission.Visibility.PUBLIC,
            status=AspirationSubmission.Status.INVESTIGATING,
            is_featured=False,
        )

        self.client.force_authenticate(user=admin)
        response = self.client.post(
            reverse("admin-aspirations:admin-aspiration-submissions-set-featured", args=[extra.pk])
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Only 6 aspirations can be featured", response.data["message"])


class AspirationPermissionTests(APITestCase):
    def setUp(self):
        self.submission = AspirationSubmission.objects.create(
            ticket_id="ASP-PERM0001",
            full_name="Permission User",
            npm="22000018",
            email="perm@example.com",
            title="Permission Ticket",
            short_description="Permission ticket",
        )
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            full_name="Regular User",
        )
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="password123",
            full_name="Admin User",
            is_staff=True,
        )

    def test_admin_submission_list_requires_authentication(self):
        response = self.client.get(reverse("admin-aspirations:admin-aspiration-submissions-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_access_admin_submission_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("admin-aspirations:admin-aspiration-submissions-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_access_admin_submission_list(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse("admin-aspirations:admin-aspiration-submissions-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
