from datetime import datetime, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from about.models import AboutSection, HeroSection
from academic.models import CountdownEvent, QuickDownloadItem, RepositoryMaterial, YouTubeSection
from analytics_dashboard.models import VisitorDailyVisit
from aspirations.models import AspirationSubmission
from aspirations.services import create_activity_log
from career.models import CareerResourceConfiguration
from competency.models import AgendaCard


class Command(BaseCommand):
    help = "Seed demo data for local development."

    def handle(self, *args, **options):
        self.seed_about()
        self.seed_academic()
        self.seed_competency()
        self.seed_career()
        self.seed_aspirations()
        self.seed_visitors()
        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))

    def seed_about(self):
        HeroSection.objects.update_or_create(
            title="Kabinet Harmoni 2026",
            defaults={
                "subtitle": "Bergerak bersama untuk kampus yang lebih hidup",
                "description": "Portal resmi kabinet untuk program, aspirasi, dan kalender kegiatan.",
                "primary_button_label": "Lihat Program",
                "primary_button_url": "https://example.com/program",
                "secondary_button_label": "Kirim Aspirasi",
                "secondary_button_url": "https://example.com/aspirasi",
                "is_active": True,
            },
        )
        AboutSection.objects.update_or_create(
            title="Tentang Kami",
            defaults={
                "subtitle": "Kabinet mahasiswa periode 2026",
                "description": "Kami berfokus pada advokasi, akademik, kompetensi, dan penguatan komunitas.",
                "is_active": True,
            },
        )

    def seed_academic(self):
        QuickDownloadItem.objects.update_or_create(
            title="Panduan KRS",
            defaults={
                "external_url": "https://example.com/panduan-krs",
                "display_order": 1,
                "is_active": True,
                "file": None,
            },
        )
        QuickDownloadItem.objects.update_or_create(
            title="Portal Akademik",
            defaults={
                "external_url": "https://example.com/portal-akademik",
                "display_order": 2,
                "is_active": True,
                "file": None,
            },
        )

        repository_items = [
            ("akuntansi", "Akuntansi Dasar", "https://drive.google.com/file/d/123/view", 1),
            ("manajemen", "Pengantar Manajemen", "https://drive.google.com/file/d/456/view", 1),
        ]
        for section, title, link, order in repository_items:
            RepositoryMaterial.objects.update_or_create(
                section=section,
                title=title,
                defaults={"google_drive_link": link, "display_order": order},
            )

        YouTubeSection.objects.update_or_create(
            title="YouTube Akademik",
            defaults={
                "description": "Video pembelajaran dan dokumentasi kegiatan.",
                "embed_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
                "embed_code": "",
                "is_active": True,
            },
        )

        CountdownEvent.objects.update_or_create(
            title="Batas Akhir KRS",
            defaults={
                "target_datetime": timezone.make_aware(
                    datetime.combine(timezone.localdate() + timedelta(days=7), time(hour=17))
                ),
                "display_order": 1,
                "is_active": True,
            },
        )

    def seed_competency(self):
        agenda_items = [
            {
                "title": "Business Case Competition 2026",
                "short_description": "Kompetisi nasional untuk mahasiswa ekonomi dan bisnis.",
                "urgency_tag": "segera",
                "recommendation_tag": "rekomendasi BEM",
                "category_tag": "lomba",
                "scope_tag": "nasional",
                "pricing_tag": "gratis",
                "deadline_date": timezone.localdate() + timedelta(days=10),
                "registration_link": "https://example.com/register-bcc",
                "google_calendar_link": "",
                "is_active": True,
                "sort_order": 1,
            },
            {
                "title": "Workshop CV Global",
                "short_description": "Pelatihan CV dan LinkedIn untuk peluang internasional.",
                "urgency_tag": "minggu ini",
                "recommendation_tag": "rekomendasi BEM",
                "category_tag": "workshop",
                "scope_tag": "internasional",
                "pricing_tag": "gratis",
                "deadline_date": timezone.localdate() + timedelta(days=14),
                "registration_link": "https://example.com/register-workshop",
                "google_calendar_link": "",
                "is_active": True,
                "sort_order": 2,
            },
        ]
        for item in agenda_items:
            AgendaCard.objects.update_or_create(title=item["title"], defaults=item)

    def seed_career(self):
        CareerResourceConfiguration.objects.update_or_create(
            cv_templates="https://example.com/cv-templates",
            defaults={
                "cover_letter": "https://example.com/cover-letter",
                "portfolio_guide": "https://example.com/portfolio-guide",
                "salary_script": "https://example.com/salary-script",
                "case_study_interview_prep": "https://example.com/case-study-interview",
                "is_active": True,
            },
        )

    def seed_aspirations(self):
        aspirations = [
            {
                "ticket_id": "ASP-AAAABBBBCC",
                "full_name": "Rina Putri",
                "npm": "22123456",
                "email": "rina@example.com",
                "title": "Perbaikan WiFi Gedung A",
                "short_description": "WiFi sering putus saat jam kuliah.",
                "status": AspirationSubmission.Status.INVESTIGATING,
                "visibility": AspirationSubmission.Visibility.PUBLIC,
                "is_featured": True,
                "upvote_count": 12,
                "vote_count": 7,
            },
            {
                "ticket_id": "ASP-DDDDEEEEFF",
                "full_name": "Anonim",
                "npm": "22123457",
                "email": "anon@example.com",
                "title": "Kebersihan Toilet Gedung B",
                "short_description": "Perlu peningkatan kebersihan dan jadwal pembersihan rutin.",
                "status": AspirationSubmission.Status.RESOLVED,
                "visibility": AspirationSubmission.Visibility.ANONYMOUS,
                "is_featured": True,
                "upvote_count": 8,
                "vote_count": 4,
            },
        ]
        for payload in aspirations:
            aspiration, created = AspirationSubmission.objects.update_or_create(
                ticket_id=payload["ticket_id"],
                defaults=payload,
            )
            if created and not aspiration.activity_logs.exists():
                create_activity_log(
                    aspiration,
                    action="submitted",
                    message="Aspiration ticket submitted",
                    actor_name=aspiration.full_name,
                    metadata={"source": "seed_demo_data"},
                )

    def seed_visitors(self):
        today = timezone.localdate()
        for offset in range(30):
            visit_date = today - timedelta(days=offset)
            for index in range((offset % 5) + 1):
                VisitorDailyVisit.objects.get_or_create(
                    visit_date=visit_date,
                    fingerprint_hash=f"seed-{visit_date.isoformat()}-{index}",
                    defaults={
                        "first_path": "/api/v1/public/core/health/",
                        "hit_count": 1,
                        "last_seen_at": timezone.make_aware(datetime.combine(visit_date, time(hour=9 + index))),
                    },
                )
