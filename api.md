# API Guide for Frontend

Dokumen ini ditujukan untuk tim frontend public site dan admin dashboard. Fokusnya adalah:

- endpoint apa saja yang tersedia saat ini
- apa yang bisa dilakukan frontend
- bentuk request/response yang perlu di-handle
- catatan perilaku backend yang penting untuk implementasi UI

Dokumen ini mengikuti route dan serializer yang aktif di codebase sekarang.

## 1. Base URL

Local development:

```txt
http://127.0.0.1:8000
```

Global development:

```txt
http://203.194.113.185/
```

Prefix semua endpoint API:

```txt
/api/v1/
```

Pembagian scope:

- Public API: `/api/v1/public/...`
- Admin API: `/api/v1/admin/...`

## 2. Ringkasnya: Frontend Bisa Apa Saja?

### Public frontend

Public frontend bisa:

- menampilkan hero section
- menampilkan section tentang kami
- menampilkan kalender kabinet dengan `embed_url` dan `embed_code`
- menampilkan profil organisasi dan daftar leadership
- menampilkan layanan akademik
- menampilkan quick downloads
- menampilkan repository bahan kuliah per section
- menampilkan section YouTube
- menampilkan countdown event
- menampilkan program kompetensi
- menampilkan agenda card kompetensi dengan filter
- menampilkan career resources
- menampilkan career opportunities
- menampilkan campaign advokasi
- menampilkan featured aspirations
- submit aspiration baru
- upvote dan vote aspiration featured
- melacak progress aspiration via `ticket_id`

### Admin frontend

Admin frontend bisa:

- login, refresh token, logout
- mengambil profil admin yang sedang login
- mengelola user admin
- mengelola konten About
- mengelola konten Academic
- mengelola konten Competency
- mengelola konten Career
- mengelola campaign Advocacy
- melihat ringkasan dashboard dan log tiket
- melihat dan mengubah aspiration submission
- mengatur featured / unfeatured aspiration

## 3. Global Response Format

Semua response sukses dibungkus dengan format:

```json
{
  "success": true,
  "message": "Request successful",
  "data": {}
}
```

Contoh error:

```json
{
  "success": false,
  "message": "Ticket not found.",
  "data": {
    "detail": "Ticket not found."
  }
}
```

## 4. Pagination Format

Endpoint list yang dipaginasi mengembalikan:

```json
{
  "success": true,
  "message": "Resources retrieved successfully",
  "data": {
    "items": [],
    "pagination": {
      "count": 0,
      "next": null,
      "previous": null,
      "page": 1,
      "page_size": 10,
      "total_pages": 1
    }
  }
}
```

Query param umum:

- `page`
- `page_size`
- `search`
- `ordering`

Catatan:

- endpoint singleton mengembalikan object langsung di `data`
- beberapa endpoint custom mengembalikan object atau array langsung di `data`, bukan `data.items`

## 5. Authentication

### Public API

- tidak membutuhkan login

### Admin API

- menggunakan JWT Bearer token
- login:

```txt
POST /api/v1/admin/accounts/auth/login/
```

Request body:

```json
{
  "email": "admin@example.com",
  "password": "your-password"
}
```

Success response:

```json
{
  "success": true,
  "message": "Authentication successful",
  "data": {
    "refresh": "jwt-refresh-token",
    "access": "jwt-access-token",
    "user": {
      "id": "uuid",
      "email": "admin@example.com",
      "full_name": "Admin User",
      "phone_number": "",
      "avatar": null,
      "role": "superadmin",
      "is_staff": true,
      "is_superuser": true,
      "is_active": true,
      "created_at": "2026-03-15T00:00:00Z",
      "updated_at": "2026-03-15T00:00:00Z"
    }
  }
}
```

Header untuk semua endpoint admin:

```txt
Authorization: Bearer <access_token>
```

Refresh token:

```txt
POST /api/v1/admin/accounts/auth/refresh/
```

Logout:

```txt
POST /api/v1/admin/accounts/auth/logout/
```

Body logout:

```json
{
  "refresh": "jwt-refresh-token"
}
```

## 6. Catatan Global Untuk Frontend

- trailing slash yang didokumentasikan di sini adalah bentuk standar yang sebaiknya dipakai frontend
- file/image bisa berupa absolute URL
- jika deployment tertentu memberi path relatif, frontend sebaiknya tetap aman dengan prepend base URL
- endpoint submit aspiration memakai `multipart/form-data`
- frontend perlu menangani `429 Too Many Requests`

Throttle penting:

- aspiration submit: `2/hour`, `5/day`
- aspiration interaction vote/upvote: `10/hour`, `30/day`
- ticket tracking: `60/hour`
- admin login: `5/min`, `20/hour`

## 7. Public API

### 7.1 Core

Apa yang bisa dilakukan frontend:

- health check backend

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | `/api/v1/public/core/health/` | Mengecek backend hidup |

### 7.2 About

Apa yang bisa dilakukan frontend:

- render hero homepage
- render section tentang kami
- render kalender kabinet
- render profil organisasi
- render daftar leadership

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | `/api/v1/public/about/hero/` | Mengambil 1 hero aktif |
| GET | `/api/v1/public/about/tentang-kami/` | Mengambil 1 about section aktif |
| GET | `/api/v1/public/about/cabinet-calendar/` | Mengambil 1 kalender kabinet aktif |
| GET | `/api/v1/public/about/profiles/` | List profil organisasi |
| GET | `/api/v1/public/about/profiles/{id}/` | Detail profil organisasi |
| GET | `/api/v1/public/about/leadership/` | List leadership |
| GET | `/api/v1/public/about/leadership/{id}/` | Detail leadership |

Contoh response hero:

```json
{
  "success": true,
  "message": "Active hero section retrieved successfully",
  "data": {
    "id": "uuid",
    "title": "Kabinet Harmoni 2026",
    "subtitle": "Bergerak bersama",
    "description": "Portal resmi kabinet",
    "image": "http://127.0.0.1:8000/media/about/hero/example.jpg",
    "primary_button_label": "Lihat Program",
    "primary_button_url": "https://example.com/program",
    "secondary_button_label": "Kirim Aspirasi",
    "secondary_button_url": "https://example.com/aspirasi"
  }
}
```

Contoh response tentang kami:

```json
{
  "success": true,
  "message": "Active about section retrieved successfully",
  "data": {
    "id": "uuid",
    "title": "Tentang Kami",
    "subtitle": "Kabinet mahasiswa",
    "description": "Deskripsi singkat organisasi",
    "image": null
  }
}
```

Contoh response cabinet calendar:

```json
{
  "success": true,
  "message": "Active cabinet calendar retrieved successfully",
  "data": {
    "id": "uuid",
    "title": "Kalender Kabinet",
    "description": "Agenda kabinet",
    "embed_url": "https://calendar.google.com/calendar/embed?...",
    "embed_code": "<iframe src=\"https://calendar.google.com/calendar/embed?...\"></iframe>",
    "provider": "google_calendar"
  }
}
```

Catatan frontend:

- `cabinet-calendar` adalah singleton, bukan list
- untuk render iframe, frontend sebaiknya tetap sanitize dengan aman
- `leadership` mendukung `search` dan `ordering`

### 7.3 Academic

Apa yang bisa dilakukan frontend:

- render layanan akademik
- render quick downloads
- render repository bahan kuliah per section
- render section YouTube
- render countdown event

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | `/api/v1/public/academic/services/` | List layanan akademik |
| GET | `/api/v1/public/academic/services/{id}/` | Detail layanan akademik |
| GET | `/api/v1/public/academic/quick-downloads/` | List quick downloads |
| GET | `/api/v1/public/academic/quick-downloads/{id}/` | Detail quick download |
| GET | `/api/v1/public/academic/repository/` | Object grouped repository: `akuntansi` dan `manajemen` |
| GET | `/api/v1/public/academic/youtube/` | 1 section YouTube aktif |
| GET | `/api/v1/public/academic/countdown-events/` | List countdown event aktif |
| GET | `/api/v1/public/academic/countdown-events/{id}/` | Detail countdown event |

Contoh quick downloads:

```json
{
  "success": true,
  "message": "Resources retrieved successfully",
  "data": {
    "items": [
      {
        "id": "uuid",
        "title": "Panduan KRS",
        "resource_type": "file",
        "resource_url": "http://127.0.0.1:8000/media/academic/quick-downloads/file.pdf",
        "display_order": 1
      }
    ],
    "pagination": {
      "count": 1,
      "next": null,
      "previous": null,
      "page": 1,
      "page_size": 10,
      "total_pages": 1
    }
  }
}
```

Contoh repository:

```json
{
  "success": true,
  "message": "Repository materials retrieved successfully",
  "data": {
    "akuntansi": [
      {
        "id": "uuid",
        "title": "Akuntansi Dasar",
        "google_drive_link": "https://drive.google.com/file/d/xxx/view",
        "display_order": 1
      }
    ],
    "manajemen": [
      {
        "id": "uuid",
        "title": "Pengantar Manajemen",
        "google_drive_link": "https://drive.google.com/file/d/yyy/view",
        "display_order": 1
      }
    ]
  }
}
```

Contoh YouTube singleton:

```json
{
  "success": true,
  "message": "Active YouTube section retrieved successfully",
  "data": {
    "id": "uuid",
    "title": "YouTube Akademik",
    "description": "Video pembelajaran dan dokumentasi",
    "embed_url": "https://www.youtube.com/embed/abc123"
  }
}
```

Catatan frontend:

- `repository` bukan endpoint paginated
- `quick-downloads` mengembalikan `resource_type` = `file` atau `external_link`
- `countdown-events` mendukung `search` dan `ordering`

### 7.4 Competency

Apa yang bisa dilakukan frontend:

- render daftar program kompetensi
- render agenda card
- memfilter agenda card sesuai tag
- render winner slide section dari maksimal 5 slot tetap

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | `/api/v1/public/competency/programs/` | List program kompetensi |
| GET | `/api/v1/public/competency/programs/{id}/` | Detail program kompetensi |
| GET | `/api/v1/public/competency/winner-slides/` | List winner slide yang sudah terisi gambar |
| GET | `/api/v1/public/competency/agenda-cards/` | List agenda card |
| GET | `/api/v1/public/competency/agenda-cards/{id}/` | Detail agenda card |

Query params penting untuk `agenda-cards`:

- `search`
- `ordering`
- `urgency_tag=true|false`
- `recommendation_tag=true|false`
- `category_tag`
- `scope_tag`
- `pricing_tag`

Contoh winner slides:

```json
{
  "success": true,
  "message": "Winner slides retrieved successfully",
  "data": {
    "items": [
      {
        "id": "uuid",
        "image_url": "http://127.0.0.1:8000/media/competency/winner-slides/slide-1.png",
        "alt_text": "Juara nasional 2026",
        "display_order": 1,
        "updated_at": "2026-04-05T21:00:00+07:00"
      }
    ],
    "pagination": {
      "count": 1,
      "next": null,
      "previous": null,
      "page": 1,
      "page_size": 10,
      "total_pages": 1
    }
  }
}
```

Catatan frontend winner slides:

- slot bersifat tetap 1 sampai 5
- endpoint public hanya mengembalikan slot yang sudah punya gambar
- gunakan `display_order` untuk urutan render di client
- gunakan `alt_text` sebagai `alt` image

Default ordering:

```txt
-created_at,-updated_at,deadline_date,title
```

Contoh item agenda card:

```json
{
  "id": "uuid",
  "title": "Business Case Competition 2026",
  "short_description": "Short description...",
  "urgency_tag": true,
  "recommendation_tag": false,
  "category_tag": "lomba",
  "scope_tag": "nasional",
  "pricing_tag": "tidak berbayar",
  "deadline_date": "2026-03-25",
  "registration_link": "https://example.com/register",
  "google_calendar_link": "https://calendar.google.com/calendar/render?...",
  "countdown_days": 10
}
```

Catatan frontend:

- `urgency_tag` dan `recommendation_tag` bertipe boolean
- `countdown_days` sudah dihitung backend

### 7.5 Career

Apa yang bisa dilakukan frontend:

- render career resources singleton
- render daftar opportunity

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | `/api/v1/public/career/resources/` | Resource links tetap untuk halaman karier |
| GET | `/api/v1/public/career/opportunities/` | List career opportunity |
| GET | `/api/v1/public/career/opportunities/{id}/` | Detail career opportunity |

Contoh response resource:

```json
{
  "success": true,
  "message": "Career resources retrieved successfully",
  "data": {
    "id": "uuid",
    "cv_templates": "https://example.com/cv-templates",
    "cover_letter": "https://example.com/cover-letter",
    "portfolio_guide": "https://example.com/portfolio-guide",
    "salary_script": "https://example.com/salary-script",
    "case_study_interview_prep": "https://example.com/case-study-interview-prep"
  }
}
```

### 7.6 Advocacy

Apa yang bisa dilakukan frontend:

- render list campaign
- render detail campaign

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | `/api/v1/public/advocacy/campaigns/` | List campaign |
| GET | `/api/v1/public/advocacy/campaigns/{id}/` | Detail campaign |

Contoh item campaign:

```json
{
  "id": "uuid",
  "title": "Campaign title",
  "slug": "campaign-title",
  "summary": "Ringkasan singkat",
  "content": "Konten lengkap campaign",
  "banner": "http://127.0.0.1:8000/media/advocacy/banner.jpg",
  "embed_url": "https://example.com/embed"
}
```

### 7.7 Aspirations

Apa yang bisa dilakukan frontend:

- menampilkan featured aspirations
- submit aspiration baru dari form public
- mengirim upvote
- mengirim vote
- tracking ticket

| Method | Endpoint | Kegunaan |
|---|---|---|
| POST | `/api/v1/public/aspirations/submit/` | Submit aspiration baru |
| GET | `/api/v1/public/aspirations/featured/` | List featured aspirations |
| POST | `/api/v1/public/aspirations/{id}/upvote/` | Tambah upvote |
| POST | `/api/v1/public/aspirations/{id}/vote/` | Tambah vote |
| GET | `/api/v1/public/tickets/track/?ticket_id=...` | Lacak status ticket |

Query param untuk `featured`:

- `visibility=public`
- `visibility=anonymous`

Request submit aspiration:

- content type: `multipart/form-data`

Fields:

- `full_name` required
- `npm` required
- `email` required
- `title` required
- `short_description` required
- `evidence_attachment` optional

Contoh response submit:

```json
{
  "success": true,
  "message": "Aspiration submitted successfully",
  "data": {
    "ticket_id": "ASP-1A2B3C4D5E",
    "title": "Perbaikan WiFi Gedung A",
    "status": "submitted",
    "submitted_at": "2026-03-15T05:30:00Z",
    "updated_at": "2026-03-15T05:30:00Z",
    "visibility": "anonymous",
    "short_description": "WiFi sering putus saat jam kuliah"
  }
}
```

Contoh featured aspirations:

```json
{
  "success": true,
  "message": "Featured aspirations retrieved successfully",
  "data": [
    {
      "id": "uuid",
      "ticket_id": "ASP-1A2B3C4D5E",
      "title": "Perbaikan WiFi Gedung A",
      "short_description": "WiFi sering putus saat jam kuliah",
      "visibility": "public",
      "sender_name": "Rina Putri",
      "status": "investigating",
      "upvote_count": 12,
      "vote_count": 7,
      "created_at": "2026-03-15T05:30:00Z"
    }
  ]
}
```

Contoh response upvote / vote:

```json
{
  "success": true,
  "message": "Aspiration upvoted successfully",
  "data": {
    "id": "uuid",
    "ticket_id": "ASP-1A2B3C4D5E",
    "upvote_count": 13,
    "vote_count": 7
  }
}
```

Contoh response tracking kosong:

```json
{
  "success": true,
  "message": "Search a ticket ID to view aspiration progress.",
  "data": {
    "ticket_id": null,
    "title": null,
    "status": null,
    "submitted_at": null,
    "updated_at": null,
    "visibility": null,
    "short_description": null
  }
}
```

Contoh response tracking ditemukan:

```json
{
  "success": true,
  "message": "Ticket tracking retrieved successfully",
  "data": {
    "ticket_id": "ASP-1A2B3C4D5E",
    "title": "Perbaikan WiFi Gedung A",
    "status": "investigating",
    "submitted_at": "2026-03-15T05:30:00Z",
    "updated_at": "2026-03-16T02:15:00Z",
    "visibility": "anonymous",
    "short_description": "WiFi sering putus saat jam kuliah"
  }
}
```

Catatan frontend:

- `sender_name` akan `null` jika `visibility=anonymous`
- endpoint tracking tidak pernah mengekspos `email` atau `npm`
- frontend sebaiknya gunakan path dengan trailing slash

### 7.8 Analytics Info

Apa yang bisa dilakukan frontend:

- hanya mengetahui bahwa analytics dashboard tidak tersedia untuk public

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | `/api/v1/public/analytics-dashboard/` | Placeholder informasi |

Contoh response:

```json
{
  "success": true,
  "message": "Analytics dashboard is only available in the admin API",
  "data": {
    "available": false
  }
}
```

## 8. Admin API

Semua endpoint admin membutuhkan bearer token, kecuali login dan refresh.

## 8.1 Accounts

Apa yang bisa dilakukan frontend admin:

- login
- refresh token
- logout
- mengambil current profile
- CRUD user admin

| Method | Endpoint | Kegunaan |
|---|---|---|
| POST | `/api/v1/admin/accounts/auth/login/` | Login |
| POST | `/api/v1/admin/accounts/auth/refresh/` | Refresh access token |
| POST | `/api/v1/admin/accounts/auth/logout/` | Logout |
| GET | `/api/v1/admin/accounts/profile/` | Current admin profile |
| GET | `/api/v1/admin/accounts/users/` | List user admin |
| POST | `/api/v1/admin/accounts/users/` | Buat user admin |
| GET | `/api/v1/admin/accounts/users/{id}/` | Detail user admin |
| PUT/PATCH | `/api/v1/admin/accounts/users/{id}/` | Update user admin |
| DELETE | `/api/v1/admin/accounts/users/{id}/` | Hapus user admin |

Filter/search users:

- `search`
- `ordering`
- `is_active`
- `is_staff`
- `is_superuser`

Catatan:

- endpoint users hanya untuk superadmin
- response user membawa field `role`

## 8.2 Dashboard

Apa yang bisa dilakukan frontend admin:

- menampilkan summary cards
- menampilkan chart visitor 30 hari
- menampilkan log aktivitas tiket terbaru

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | `/api/v1/admin/dashboard/summary/` | Ringkasan dashboard |
| GET | `/api/v1/admin/dashboard/ticket-log/` | Log aktivitas tiket |

Contoh summary:

```json
{
  "success": true,
  "message": "Dashboard summary retrieved successfully",
  "data": {
    "cards": {
      "total_aspiration_submissions": 128,
      "status_counts": {
        "submitted": 41,
        "investigating": 56,
        "resolved": 31
      },
      "total_featured_aspirations": 6,
      "total_visitors_last_30_days": 842
    },
    "charts": {
      "daily_visitors_last_30_days": [
        {
          "date": "2026-02-15",
          "count": 21
        }
      ]
    }
  }
}
```

## 8.3 About

Apa yang bisa dilakukan frontend admin:

- CRUD organization profile
- CRUD leadership
- CRUD hero
- get/update cabinet calendar singleton

| Method | Endpoint |
|---|---|
| GET/POST | `/api/v1/admin/about/profiles/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/about/profiles/{id}/` |
| GET/POST | `/api/v1/admin/about/leadership/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/about/leadership/{id}/` |
| GET/POST | `/api/v1/admin/about/heroes/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/about/heroes/{id}/` |
| GET | `/api/v1/admin/about/cabinet-calendar/` |
| PUT/PATCH | `/api/v1/admin/about/cabinet-calendar/` |

Filter/search:

- `profiles`: `is_active`, `search`, `ordering`
- `leadership`: `is_active`, `search`, `ordering`
- `heroes`: `is_active`, `search`, `ordering`

Catatan:

- `cabinet-calendar` adalah singleton
- field utamanya: `title`, `description`, `embed_url`, `embed_code`

## 8.4 Academic

Apa yang bisa dilakukan frontend admin:

- CRUD academic services
- CRUD quick downloads
- CRUD repository materials
- CRUD YouTube section
- CRUD countdown events

| Method | Endpoint |
|---|---|
| GET/POST | `/api/v1/admin/academic/services/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/academic/services/{id}/` |
| GET/POST | `/api/v1/admin/academic/quick-downloads/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/academic/quick-downloads/{id}/` |
| GET/POST | `/api/v1/admin/academic/repository-materials/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/academic/repository-materials/{id}/` |
| GET/POST | `/api/v1/admin/academic/youtube-sections/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/academic/youtube-sections/{id}/` |
| GET/POST | `/api/v1/admin/academic/countdown-events/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/academic/countdown-events/{id}/` |

Filter/search:

- `services`: `is_published`, `search`, `ordering`
- `quick-downloads`: `is_active`, `search`, `ordering`
- `repository-materials`: `section`, `search`, `ordering`
- `youtube-sections`: `is_active`, `search`, `ordering`
- `countdown-events`: `is_active`, `search`, `ordering`

Business rules:

- quick downloads maksimal 5 item
- repository `akuntansi` maksimal 3 item
- repository `manajemen` maksimal 3 item
- quick download harus pilih salah satu: file atau external URL

## 8.5 Competency

Apa yang bisa dilakukan frontend admin:

- CRUD competency programs
- CRUD agenda cards

| Method | Endpoint |
|---|---|
| GET/POST | `/api/v1/admin/competency/programs/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/competency/programs/{id}/` |
| GET | `/api/v1/admin/competency/winner-slides/` |
| GET/PATCH | `/api/v1/admin/competency/winner-slides/{id}/` |
| GET/POST | `/api/v1/admin/competency/agenda-cards/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/competency/agenda-cards/{id}/` |

Filter/search:

- `programs`: `is_published`, `search`, `ordering`
- `winner-slides`: `display_order`, `search`, `ordering`
- `agenda-cards`: `is_active`, `urgency_tag`, `recommendation_tag`, `category_tag`, `scope_tag`, `pricing_tag`, `search`, `ordering`

Business rules:

- agenda cards maksimal 15
- winner slide maksimal 5 slot tetap, admin hanya update `image` dan `alt_text`
- `category_tag`: `workshop` atau `lomba`
- `scope_tag`: `nasional` atau `internasional`
- `pricing_tag`: `berbayar` atau `tidak berbayar`

## 8.6 Career

Apa yang bisa dilakukan frontend admin:

- CRUD opportunities
- CRUD resource configuration

| Method | Endpoint |
|---|---|
| GET/POST | `/api/v1/admin/career/opportunities/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/career/opportunities/{id}/` |
| GET/POST | `/api/v1/admin/career/resources/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/career/resources/{id}/` |

Filter/search:

- `opportunities`: `is_published`, `search`, `ordering`
- `resources`: `is_active`, `ordering`

## 8.7 Advocacy

Apa yang bisa dilakukan frontend admin:

- CRUD campaign

| Method | Endpoint |
|---|---|
| GET/POST | `/api/v1/admin/advocacy/campaigns/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/advocacy/campaigns/{id}/` |

Filter/search:

- `is_published`
- `search`
- `ordering`

## 8.8 Aspirations

Apa yang bisa dilakukan frontend admin:

- melihat list submission
- melihat detail submission
- update status/visibility/featured
- set featured
- unset featured

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | `/api/v1/admin/aspirations/submissions/` | List submission |
| GET | `/api/v1/admin/aspirations/submissions/{id}/` | Detail submission |
| PATCH | `/api/v1/admin/aspirations/submissions/{id}/` | Update submission |
| POST | `/api/v1/admin/aspirations/submissions/{id}/set-featured/` | Tandai featured |
| POST | `/api/v1/admin/aspirations/submissions/{id}/unset-featured/` | Lepas featured |

Filter/search:

- `search`
- `ordering`
- `status`
- `visibility`
- `is_featured`

Contoh item list admin:

```json
{
  "id": "uuid",
  "ticket_id": "ASP-1A2B3C4D5E",
  "full_name": "Rina Putri",
  "npm": "22123456",
  "email": "rina@example.com",
  "title": "Perbaikan WiFi Gedung A",
  "status": "submitted",
  "visibility": "anonymous",
  "is_featured": false,
  "upvote_count": 12,
  "vote_count": 7,
  "created_at": "2026-03-15T05:30:00Z",
  "updated_at": "2026-03-15T05:30:00Z"
}
```

Business rules:

- featured maksimal 6 item
- hanya status `investigating` atau `resolved` yang boleh menjadi featured

## 9. Saran Implementasi Frontend

- untuk endpoint list, cek dulu apakah data ada di `data.items`
- untuk endpoint singleton, baca data langsung dari `data`
- jangan asumsikan semua list endpoint punya bentuk yang sama
- untuk field media/file, handle `null`
- untuk aspiration tracking, jangan berharap data sensitif seperti `email` atau `npm`
- untuk embed URL / embed code, lakukan sanitasi render di frontend

Contoh generic type yang aman:

```ts
type ApiResponse<T> = {
  success: boolean;
  message: string;
  data: T;
};
```

Contoh paginated:

```ts
type Paginated<T> = {
  items: T[];
  pagination: {
    count: number;
    next: string | null;
    previous: string | null;
    page: number;
    page_size: number;
    total_pages: number;
  };
};
```

## 10. Useful Docs

- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`
- Raw OpenAPI schema: `/api/schema/`
