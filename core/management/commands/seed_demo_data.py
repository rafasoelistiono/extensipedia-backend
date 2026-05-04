from datetime import datetime, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from about.models import AboutSection, HeroSection
from academic.models import (
    AcademicDigitalResourceConfiguration,
    CountdownEvent,
    QuickDownloadItem,
    RepositoryMaterial,
    YouTubeSection,
)
from analytics_dashboard.models import VisitorDailyVisit
from advocacy.models import AdvocacyPolicyResourceConfiguration
from aspirations.models import AspirationSubmission
from aspirations.services import create_activity_log
from career.models import CareerResourceConfiguration
from competency.models import AgendaCard


class Command(BaseCommand):
    help = "Seed demo data for local development."

    @staticmethod
    def build_agenda_description(topic, audience, highlight):
        description = (
            f"{topic} dirancang untuk {audience}. Agenda ini merangkum manfaat utama, alur pendaftaran, "
            f"dokumen yang perlu disiapkan, dan fokus persiapan agar peserta lebih siap menghadapi deadline. "
            f"{highlight}"
        )
        if len(description) > 300:
            return f"{description[:297].rstrip()}..."
        return description

    def handle(self, *args, **options):
        self.seed_about()
        self.seed_academic()
        self.seed_competency()
        self.seed_career()
        self.seed_advocacy()
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
            ("akuntansi", "Akuntansi Keuangan Menengah", "https://drive.google.com/file/d/124/view", 2),
            ("akuntansi", "Akuntansi Biaya", "https://drive.google.com/file/d/125/view", 3),
            ("manajemen", "Pengantar Manajemen", "https://drive.google.com/file/d/456/view", 1),
            ("manajemen", "Manajemen Pemasaran", "https://drive.google.com/file/d/457/view", 2),
            ("manajemen", "Manajemen Operasional", "https://drive.google.com/file/d/458/view", 3),
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

        AcademicDigitalResourceConfiguration.objects.update_or_create(
            canva_pro_ekstensi="https://example.com/canva-pro-ekstensi",
            defaults={
                "gemini_advanced": "https://example.com/gemini-advanced",
                "is_active": True,
            },
        )

    def seed_competency(self):
        agenda_items = [
            {
                "title": "Business Case Competition 2026",
                "short_description": self.build_agenda_description(
                    "Business Case Competition 2026",
                    "mahasiswa ekonomi dan bisnis yang ingin menambah pengalaman kompetitif tingkat nasional",
                    "Peserta juga didorong menyiapkan analisis pasar, strategi implementasi, dan simulasi presentasi tim.",
                ),
                "urgency_tag": True,
                "recommendation_tag": True,
                "category_tag": "lomba",
                "scope_tag": "nasional",
                "pricing_tag": "tidak berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=10),
                "registration_link": "https://example.com/register-bcc",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "Data Analytics Challenge",
                "short_description": self.build_agenda_description(
                    "Data Analytics Challenge",
                    "mahasiswa yang ingin mengasah analisis data, visualisasi, dan penyusunan insight bisnis",
                    "Peserta menyiapkan dataset, notebook analisis, dan ringkasan rekomendasi berbasis temuan utama.",
                ),
                "urgency_tag": True,
                "recommendation_tag": True,
                "category_tag": "lomba",
                "scope_tag": "nasional",
                "pricing_tag": "tidak berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=18),
                "registration_link": "https://example.com/register-data-analytics",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "Essay Competition Ekonomi Digital",
                "short_description": self.build_agenda_description(
                    "Essay Competition Ekonomi Digital",
                    "peserta yang tertarik menulis gagasan tentang transformasi bisnis dan kebijakan digital",
                    "Tulisan perlu memuat argumen jelas, rujukan kredibel, dan solusi yang relevan untuk konteks Indonesia.",
                ),
                "urgency_tag": False,
                "recommendation_tag": True,
                "category_tag": "lomba",
                "scope_tag": "nasional",
                "pricing_tag": "berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=21),
                "registration_link": "https://example.com/register-essay-digital",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "Workshop CV Global",
                "short_description": self.build_agenda_description(
                    "Workshop CV Global",
                    "peserta yang sedang menyiapkan CV, LinkedIn, dan strategi aplikasi untuk peluang internasional",
                    "Materi akan menekankan penyusunan narasi pengalaman, penyesuaian kata kunci, dan review kesalahan umum yang sering membuat aplikasi kurang menonjol.",
                ),
                "urgency_tag": False,
                "recommendation_tag": True,
                "category_tag": "workshop",
                "scope_tag": "internasional",
                "pricing_tag": "berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=14),
                "registration_link": "https://example.com/register-workshop",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "Workshop Personal Branding LinkedIn",
                "short_description": self.build_agenda_description(
                    "Workshop Personal Branding LinkedIn",
                    "mahasiswa yang ingin membangun profil profesional dan memperluas jejaring karier",
                    "Sesi mencakup optimasi headline, ringkasan pengalaman, portofolio, dan strategi interaksi dengan rekruter.",
                ),
                "urgency_tag": False,
                "recommendation_tag": True,
                "category_tag": "workshop",
                "scope_tag": "nasional",
                "pricing_tag": "tidak berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=16),
                "registration_link": "https://example.com/register-linkedin-branding",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "Pitch Deck Bootcamp",
                "short_description": self.build_agenda_description(
                    "Pitch Deck Bootcamp",
                    "tim rintisan bisnis mahasiswa yang sedang menyiapkan proposal dan presentasi investor",
                    "Materi menekankan problem framing, model bisnis, traction, proyeksi sederhana, dan storytelling visual.",
                ),
                "urgency_tag": True,
                "recommendation_tag": False,
                "category_tag": "workshop",
                "scope_tag": "nasional",
                "pricing_tag": "berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=9),
                "registration_link": "https://example.com/register-pitch-deck",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "UI UX Design Sprint Competition",
                "short_description": self.build_agenda_description(
                    "UI UX Design Sprint Competition",
                    "mahasiswa yang ingin menguji kemampuan riset pengguna, ideasi, wireframe, dan prototyping",
                    "Peserta diminta menyusun problem statement, alur solusi, prototype, dan alasan desain yang terukur.",
                ),
                "urgency_tag": False,
                "recommendation_tag": True,
                "category_tag": "lomba",
                "scope_tag": "nasional",
                "pricing_tag": "tidak berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=24),
                "registration_link": "https://example.com/register-uiux-sprint",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "International Marketing Plan Challenge",
                "short_description": self.build_agenda_description(
                    "International Marketing Plan Challenge",
                    "peserta yang ingin menyusun strategi pemasaran lintas negara dengan pendekatan riset pasar",
                    "Tim perlu menyiapkan segmentasi, positioning, channel plan, estimasi anggaran, dan metrik keberhasilan.",
                ),
                "urgency_tag": True,
                "recommendation_tag": True,
                "category_tag": "lomba",
                "scope_tag": "internasional",
                "pricing_tag": "berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=12),
                "registration_link": "https://example.com/register-marketing-plan",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "Excel Financial Modeling Clinic",
                "short_description": self.build_agenda_description(
                    "Excel Financial Modeling Clinic",
                    "mahasiswa yang ingin memperkuat kemampuan spreadsheet untuk proyeksi keuangan dan valuasi dasar",
                    "Latihan berfokus pada struktur model, asumsi, sensitivitas, dan pengecekan error sebelum presentasi.",
                ),
                "urgency_tag": False,
                "recommendation_tag": True,
                "category_tag": "workshop",
                "scope_tag": "nasional",
                "pricing_tag": "berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=20),
                "registration_link": "https://example.com/register-financial-modeling",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "Debate Championship Public Policy",
                "short_description": self.build_agenda_description(
                    "Debate Championship Public Policy",
                    "mahasiswa yang ingin melatih argumentasi, riset isu publik, dan respons cepat dalam forum debat",
                    "Persiapan mencakup case building, latihan rebuttal, pembagian peran, dan review bukti pendukung.",
                ),
                "urgency_tag": True,
                "recommendation_tag": False,
                "category_tag": "lomba",
                "scope_tag": "nasional",
                "pricing_tag": "tidak berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=8),
                "registration_link": "https://example.com/register-policy-debate",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "Product Management Mini Course",
                "short_description": self.build_agenda_description(
                    "Product Management Mini Course",
                    "mahasiswa yang ingin memahami discovery, prioritisasi fitur, roadmap, dan komunikasi produk",
                    "Peserta akan membuat problem brief, user story, prioritas backlog, dan metrik sederhana untuk validasi.",
                ),
                "urgency_tag": False,
                "recommendation_tag": True,
                "category_tag": "workshop",
                "scope_tag": "internasional",
                "pricing_tag": "berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=27),
                "registration_link": "https://example.com/register-product-management",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "Social Innovation Hackathon",
                "short_description": self.build_agenda_description(
                    "Social Innovation Hackathon",
                    "tim yang ingin merancang solusi sosial berbasis teknologi, riset lapangan, dan validasi cepat",
                    "Tim menyiapkan prototype, dampak yang ingin dicapai, rencana implementasi, dan pitch singkat.",
                ),
                "urgency_tag": False,
                "recommendation_tag": True,
                "category_tag": "lomba",
                "scope_tag": "nasional",
                "pricing_tag": "tidak berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=25),
                "registration_link": "https://example.com/register-social-hackathon",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "Public Speaking Masterclass",
                "short_description": self.build_agenda_description(
                    "Public Speaking Masterclass",
                    "mahasiswa yang ingin meningkatkan kejelasan presentasi, gestur, struktur pesan, dan percaya diri",
                    "Sesi praktik mencakup latihan pembukaan, storytelling, pengelolaan gugup, dan umpan balik singkat.",
                ),
                "urgency_tag": False,
                "recommendation_tag": False,
                "category_tag": "workshop",
                "scope_tag": "nasional",
                "pricing_tag": "tidak berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=30),
                "registration_link": "https://example.com/register-public-speaking",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "Accounting Olympiad",
                "short_description": self.build_agenda_description(
                    "Accounting Olympiad",
                    "mahasiswa akuntansi yang ingin menguji pemahaman standar, jurnal, pelaporan, dan analisis kasus",
                    "Peserta perlu mengulang konsep dasar, latihan soal, dan strategi manajemen waktu selama babak seleksi.",
                ),
                "urgency_tag": True,
                "recommendation_tag": True,
                "category_tag": "lomba",
                "scope_tag": "nasional",
                "pricing_tag": "berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=11),
                "registration_link": "https://example.com/register-accounting-olympiad",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "Research Paper Competition",
                "short_description": self.build_agenda_description(
                    "Research Paper Competition",
                    "mahasiswa yang sedang mengembangkan ide riset ekonomi, manajemen, akuntansi, atau bisnis digital",
                    "Naskah perlu memuat latar belakang kuat, metode yang tepat, analisis data, dan kontribusi temuan.",
                ),
                "urgency_tag": False,
                "recommendation_tag": True,
                "category_tag": "lomba",
                "scope_tag": "internasional",
                "pricing_tag": "berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=35),
                "registration_link": "https://example.com/register-research-paper",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "Python for Business Workshop",
                "short_description": self.build_agenda_description(
                    "Python for Business Workshop",
                    "mahasiswa yang ingin memakai Python untuk otomasi laporan, pembersihan data, dan analisis sederhana",
                    "Peserta akan berlatih membaca file, mengolah data tabular, membuat grafik, dan menulis script reusable.",
                ),
                "urgency_tag": False,
                "recommendation_tag": True,
                "category_tag": "workshop",
                "scope_tag": "nasional",
                "pricing_tag": "tidak berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=19),
                "registration_link": "https://example.com/register-python-business",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "Entrepreneurship Idea Competition",
                "short_description": self.build_agenda_description(
                    "Entrepreneurship Idea Competition",
                    "mahasiswa yang ingin mengembangkan ide usaha dari validasi masalah sampai rencana komersialisasi",
                    "Proposal perlu memuat target pengguna, nilai solusi, model pendapatan, validasi awal, dan kebutuhan tim.",
                ),
                "urgency_tag": True,
                "recommendation_tag": False,
                "category_tag": "lomba",
                "scope_tag": "nasional",
                "pricing_tag": "tidak berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=13),
                "registration_link": "https://example.com/register-entrepreneurship-idea",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "TOEFL Preparation Intensive",
                "short_description": self.build_agenda_description(
                    "TOEFL Preparation Intensive",
                    "peserta yang menargetkan beasiswa, exchange, atau program internasional dengan syarat bahasa Inggris",
                    "Agenda mencakup diagnosis kemampuan, strategi tiap section, latihan terukur, dan rencana belajar mandiri.",
                ),
                "urgency_tag": False,
                "recommendation_tag": True,
                "category_tag": "workshop",
                "scope_tag": "internasional",
                "pricing_tag": "berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=28),
                "registration_link": "https://example.com/register-toefl-intensive",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "Sustainability Case Challenge",
                "short_description": self.build_agenda_description(
                    "Sustainability Case Challenge",
                    "mahasiswa yang ingin menyusun solusi bisnis dengan perspektif keberlanjutan dan dampak sosial",
                    "Tim perlu menimbang aspek lingkungan, finansial, operasional, dan komunikasi dampak secara seimbang.",
                ),
                "urgency_tag": True,
                "recommendation_tag": True,
                "category_tag": "lomba",
                "scope_tag": "internasional",
                "pricing_tag": "tidak berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=15),
                "registration_link": "https://example.com/register-sustainability-case",
                "google_calendar_link": "",
                "is_active": True,
            },
            {
                "title": "Negotiation Skill Lab",
                "short_description": self.build_agenda_description(
                    "Negotiation Skill Lab",
                    "mahasiswa yang ingin melatih negosiasi, penyusunan posisi, dan komunikasi saat diskusi profesional",
                    "Latihan mencakup simulasi peran, pemetaan kepentingan, strategi konsesi, dan evaluasi hasil negosiasi.",
                ),
                "urgency_tag": False,
                "recommendation_tag": False,
                "category_tag": "workshop",
                "scope_tag": "nasional",
                "pricing_tag": "berbayar",
                "deadline_date": timezone.localdate() + timedelta(days=32),
                "registration_link": "https://example.com/register-negotiation-lab",
                "google_calendar_link": "",
                "is_active": True,
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

    def seed_advocacy(self):
        AdvocacyPolicyResourceConfiguration.objects.update_or_create(
            siak_war="https://example.com/siak-war",
            defaults={
                "cicilan_ukt": "https://example.com/cicilan-ukt",
                "alur_skpi": "https://example.com/alur-skpi",
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
