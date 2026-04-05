import base64
from datetime import timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from dashboard.forms import AgendaCardForm

from competency.models import AgendaCard, CompetencyWinnerSlide


def unwrap_response_data(response):
    payload = response.data
    while isinstance(payload, dict):
        if "data" in payload:
            payload = payload["data"]
            continue
        if "items" in payload:
            payload = payload["items"]
            continue
        if "results" in payload:
            payload = payload["results"]
            continue
        break
    return payload


def build_short_description(seed):
    return (
        f"{seed} memberi ringkasan singkat tentang manfaat kegiatan, target peserta, dokumen penting, "
        f"dan langkah persiapan utama agar pendaftaran lebih terarah serta hasil program bisa dipakai "
        f"untuk penguatan portofolio akademik maupun profesional."
    )


def build_test_image(name="slide.png"):
    return SimpleUploadedFile(
        name,
        base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9p6k9TQAAAAASUVORK5CYII="
        ),
        content_type="image/png",
    )


class AgendaCardModelTests(TestCase):
    def test_short_description_rejects_text_over_300_characters(self):
        agenda = AgendaCard(
            title="Agenda Singkat",
            short_description="a" * 301,
            urgency_tag=True,
            recommendation_tag=False,
            category_tag=AgendaCard.CategoryTag.WORKSHOP,
            scope_tag=AgendaCard.ScopeTag.NASIONAL,
            pricing_tag=AgendaCard.PricingTag.BERBAYAR,
            deadline_date=timezone.localdate() + timedelta(days=7),
            registration_link="https://example.com/register",
        )

        with self.assertRaises(ValidationError):
            agenda.full_clean()


class AgendaCardFormTests(TestCase):
    def test_boolean_fields_use_radio_inputs(self):
        form = AgendaCardForm()

        self.assertIsInstance(form.fields["urgency_tag"].widget, forms.RadioSelect)
        self.assertIsInstance(form.fields["recommendation_tag"].widget, forms.RadioSelect)
        self.assertEqual(form.fields["urgency_tag"].choices, [(True, "True"), (False, "False")])


class AgendaCardPublicApiTests(APITestCase):
    def test_public_agenda_cards_are_ordered_by_newest_first_and_support_boolean_filter(self):
        older = AgendaCard.objects.create(
            title="Older Agenda",
            short_description=build_short_description("Older agenda"),
            urgency_tag=False,
            recommendation_tag=True,
            category_tag=AgendaCard.CategoryTag.LOMBA,
            scope_tag=AgendaCard.ScopeTag.NASIONAL,
            pricing_tag=AgendaCard.PricingTag.TIDAK_BERBAYAR,
            deadline_date=timezone.localdate() + timedelta(days=20),
            registration_link="https://example.com/older",
            is_active=True,
        )
        newer = AgendaCard.objects.create(
            title="Newer Agenda",
            short_description=build_short_description("Newer agenda"),
            urgency_tag=True,
            recommendation_tag=False,
            category_tag=AgendaCard.CategoryTag.WORKSHOP,
            scope_tag=AgendaCard.ScopeTag.INTERNASIONAL,
            pricing_tag=AgendaCard.PricingTag.BERBAYAR,
            deadline_date=timezone.localdate() + timedelta(days=10),
            registration_link="https://example.com/newer",
            is_active=True,
        )

        AgendaCard.objects.filter(pk=older.pk).update(created_at=timezone.now() - timedelta(days=2))
        AgendaCard.objects.filter(pk=newer.pk).update(created_at=timezone.now())

        response = self.client.get(
            f"{reverse('public-competency:public-agenda-cards-list')}?urgency_tag=true"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = unwrap_response_data(response)
        self.assertEqual(payload[0]["title"], "Newer Agenda")
        self.assertTrue(all(item["urgency_tag"] is True for item in payload))


class CompetencyWinnerSlideModelTests(TestCase):
    def test_winner_slide_slots_are_seeded_to_five_records(self):
        self.assertEqual(CompetencyWinnerSlide.objects.count(), CompetencyWinnerSlide.MAX_RECORDS)
        self.assertEqual(
            list(CompetencyWinnerSlide.objects.order_by("display_order").values_list("display_order", flat=True)),
            [1, 2, 3, 4, 5],
        )


class CompetencyWinnerSlidePublicApiTests(APITestCase):
    def test_public_winner_slides_only_return_filled_slots_in_slot_order(self):
        visible = CompetencyWinnerSlide.objects.get(display_order=2)
        visible.image = build_test_image("visible.png")
        visible.alt_text = "Visible alt"
        visible.save()

        response = self.client.get(reverse("public-competency:public-competency-winner-slides-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = unwrap_response_data(response)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["id"], str(visible.id))
        self.assertEqual(payload[0]["display_order"], 2)
        self.assertTrue(payload[0]["image_url"].endswith(".png"))
