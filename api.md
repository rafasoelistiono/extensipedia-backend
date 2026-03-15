# API Guide for Frontend Engineer

Dokumen ini merangkum endpoint backend yang relevan untuk frontend web/admin. Fokusnya adalah konsumsi API yang sudah ada sekarang, bukan spesifikasi ideal.

## Base URL

Local development:

```txt
http://127.0.0.1:8000
```

API version prefix:

```txt
/api/v1/
```

## API Scopes

- Public/client API: `/api/v1/public/...`
- Admin API: `/api/v1/admin/...`

## Global Response Format

Semua response sukses dan error dibungkus dengan format standar:

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

## Pagination Format

Endpoint list yang dipaginasi akan mengembalikan:

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

Query params umum:

- `page`
- `page_size`
- `search`
- `ordering`
- beberapa endpoint admin/public juga mendukung filter spesifik via query param

## Authentication

### Public API

- Tidak butuh login

### Admin API

- Menggunakan JWT Bearer token
- Login endpoint:

```txt
POST /api/v1/admin/accounts/auth/login/
```

Request:

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

Header untuk endpoint admin:

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

Body:

```json
{
  "refresh": "jwt-refresh-token"
}
```

## Throttling Notes

Beberapa endpoint public punya throttle yang cukup ketat:

- Aspiration submit: `2/hour`, `5/day`
- Aspiration vote/upvote: `10/hour`, `30/day`
- Ticket tracking: `60/hour`
- Admin login: `5/min`, `20/hour`

Frontend sebaiknya menangani `429 Too Many Requests` secara eksplisit.

## Media/File Notes

- File/image field bisa berupa URL absolut.
- Jika di deployment tertentu keluar sebagai path relatif, frontend sebaiknya tetap aman dengan fallback penggabungan base URL.

## Public API Endpoints

### Core

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/v1/public/core/health/` | Health check |

### About

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/v1/public/about/hero/` | Single active hero |
| GET | `/api/v1/public/about/tentang-kami/` | Single active about section |
| GET | `/api/v1/public/about/profiles/` | Organization profiles list |
| GET | `/api/v1/public/about/profiles/{id}/` | Organization profile detail |
| GET | `/api/v1/public/about/leadership/` | Leadership list |
| GET | `/api/v1/public/about/leadership/{id}/` | Leadership detail |
| GET | `/api/v1/public/about/cabinet-calendars/` | Active cabinet calendars |
| GET | `/api/v1/public/about/cabinet-calendars/{id}/` | Cabinet calendar detail |

#### Hero response

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

#### Tentang Kami response

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

### Academic

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/v1/public/academic/services/` | Academic services list |
| GET | `/api/v1/public/academic/services/{id}/` | Academic service detail |
| GET | `/api/v1/public/academic/quick-downloads/` | Max 5 items |
| GET | `/api/v1/public/academic/quick-downloads/{id}/` | Detail |
| GET | `/api/v1/public/academic/repository/` | Grouped by `akuntansi` and `manajemen` |
| GET | `/api/v1/public/academic/youtube/` | Single active YouTube section |
| GET | `/api/v1/public/academic/countdown-events/` | Active countdown events |
| GET | `/api/v1/public/academic/countdown-events/{id}/` | Detail |

#### Quick Downloads response

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

#### Repository response

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

#### YouTube response

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

#### Countdown response item

```json
{
  "id": "uuid",
  "title": "Batas Akhir KRS",
  "target_datetime": "2026-03-20T17:00:00+07:00",
  "display_order": 1
}
```

### Competency

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/v1/public/competency/programs/` | Programs list |
| GET | `/api/v1/public/competency/programs/{id}/` | Program detail |
| GET | `/api/v1/public/competency/agenda-cards/` | Max 15 total records |
| GET | `/api/v1/public/competency/agenda-cards/{id}/` | Agenda card detail |

Supported query params for `agenda-cards`:

- `search`
- `ordering`
- `urgency_tag`
- `recommendation_tag`
- `category_tag`
- `scope_tag`
- `pricing_tag`

Default ordering:

```txt
sort_order, deadline_date, title
```

#### Agenda card response item

```json
{
  "id": "uuid",
  "title": "Business Case Competition 2026",
  "short_description": "Kompetisi nasional untuk mahasiswa",
  "urgency_tag": "segera",
  "recommendation_tag": "rekomendasi BEM",
  "category_tag": "lomba",
  "scope_tag": "nasional",
  "pricing_tag": "gratis",
  "deadline_date": "2026-03-25",
  "registration_link": "https://example.com/register",
  "google_calendar_link": "https://calendar.google.com/calendar/render?...",
  "sort_order": 1,
  "countdown_days": 10
}
```

### Career

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/v1/public/career/resources/` | Fixed resource keys |
| GET | `/api/v1/public/career/opportunities/` | Opportunity list |
| GET | `/api/v1/public/career/opportunities/{id}/` | Opportunity detail |

#### Career resources response

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

### Advocacy

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/v1/public/advocacy/campaigns/` | Published campaigns |
| GET | `/api/v1/public/advocacy/campaigns/{id}/` | Campaign detail |

### Aspirations

| Method | Endpoint | Notes |
|---|---|---|
| POST | `/api/v1/public/aspirations/submit/` | Public aspiration submission |
| GET | `/api/v1/public/aspirations/featured/` | Up to 6 featured aspirations |
| POST | `/api/v1/public/aspirations/{id}/upvote/` | Atomic increment |
| POST | `/api/v1/public/aspirations/{id}/vote/` | Atomic increment |
| GET | `/api/v1/public/tickets/track/?ticket_id=...` | Public-safe tracking |

Supported query params for featured list:

- `visibility=public`
- `visibility=anonymous`

#### Aspiration submit request

`multipart/form-data`

Fields:

- `full_name` required
- `npm` required
- `email` required
- `title` required
- `short_description` required
- `evidence_attachment` optional, image/pdf, max 5 MB

#### Aspiration submit success response

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

#### Featured aspirations response

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

Catatan:

- Jika `visibility=anonymous`, `sender_name` akan `null`
- Hanya aspiration featured dengan status `investigating` atau `resolved` yang muncul di endpoint public

#### Upvote/Vote response

Response body mengembalikan featured aspiration yang sudah ter-update:

```json
{
  "success": true,
  "message": "Aspiration upvoted successfully",
  "data": {
    "id": "uuid",
    "ticket_id": "ASP-1A2B3C4D5E",
    "title": "Perbaikan WiFi Gedung A",
    "short_description": "WiFi sering putus saat jam kuliah",
    "visibility": "public",
    "sender_name": "Rina Putri",
    "status": "investigating",
    "upvote_count": 13,
    "vote_count": 7,
    "created_at": "2026-03-15T05:30:00Z"
  }
}
```

#### Ticket tracking response

Empty query:

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

Found ticket:

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

Tracking endpoint tidak pernah mengekspos:

- `email`
- `npm`
- admin internal note

### Analytics Info

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/v1/public/analytics-dashboard/` | Public placeholder only |

Response:

```json
{
  "success": true,
  "message": "Analytics dashboard is only available in the admin API",
  "data": {
    "available": false
  }
}
```

## Admin API Endpoints

Semua endpoint admin butuh `Authorization: Bearer <access_token>` kecuali login dan refresh.

### Accounts

| Method | Endpoint | Notes |
|---|---|---|
| POST | `/api/v1/admin/accounts/auth/login/` | Login |
| POST | `/api/v1/admin/accounts/auth/refresh/` | Refresh JWT |
| POST | `/api/v1/admin/accounts/auth/logout/` | Logout |
| GET | `/api/v1/admin/accounts/profile/` | Current admin profile |
| GET | `/api/v1/admin/accounts/users/` | Superadmin only |
| POST | `/api/v1/admin/accounts/users/` | Superadmin only |
| GET | `/api/v1/admin/accounts/users/{id}/` | Superadmin only |
| PUT/PATCH | `/api/v1/admin/accounts/users/{id}/` | Superadmin only |
| DELETE | `/api/v1/admin/accounts/users/{id}/` | Superadmin only |

Supported query params for users:

- `search`
- `ordering`
- `is_active`
- `is_staff`
- `is_superuser`

### Dashboard

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/v1/admin/dashboard/summary/` | Summary cards + chart-ready visitors |
| GET | `/api/v1/admin/dashboard/ticket-log/` | Recent ticket activity |

#### Dashboard summary response

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

#### Ticket log response

```json
{
  "success": true,
  "message": "Ticket activity log retrieved successfully",
  "data": [
    {
      "id": "uuid",
      "ticket_id": "ASP-1A2B3C4D5E",
      "title": "Perbaikan WiFi Gedung A",
      "action": "updated",
      "message": "Aspiration ticket updated",
      "actor_name": "Admin Utama",
      "status_snapshot": "investigating",
      "visibility_snapshot": "anonymous",
      "metadata": {
        "changed_fields": [
          "status",
          "visibility"
        ]
      },
      "created_at": "2026-03-15T12:10:00Z"
    }
  ]
}
```

### About

| Method | Endpoint |
|---|---|
| GET/POST | `/api/v1/admin/about/profiles/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/about/profiles/{id}/` |
| GET/POST | `/api/v1/admin/about/leadership/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/about/leadership/{id}/` |
| GET/POST | `/api/v1/admin/about/heroes/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/about/heroes/{id}/` |
| GET/POST | `/api/v1/admin/about/tentang-kami/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/about/tentang-kami/{id}/` |
| GET/POST | `/api/v1/admin/about/cabinet-calendars/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/about/cabinet-calendars/{id}/` |

Useful filters/search:

- `profiles`: `is_active`, `search`, `ordering`
- `leadership`: `is_active`, `search`, `ordering`
- `heroes`: `is_active`, `search`, `ordering`
- `tentang-kami`: `is_active`, `search`, `ordering`
- `cabinet-calendars`: `is_active`, `provider`, `search`, `ordering`

### Academic

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

Useful filters/search:

- `services`: `is_published`, `search`, `ordering`
- `quick-downloads`: `is_active`, `search`, `ordering`
- `repository-materials`: `section`, `search`, `ordering`
- `youtube-sections`: `is_active`, `search`, `ordering`
- `countdown-events`: `is_active`, `search`, `ordering`

Business rules:

- Quick downloads max 5
- Repository `akuntansi` max 3
- Repository `manajemen` max 3

### Competency

| Method | Endpoint |
|---|---|
| GET/POST | `/api/v1/admin/competency/programs/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/competency/programs/{id}/` |
| GET/POST | `/api/v1/admin/competency/agenda-cards/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/competency/agenda-cards/{id}/` |

Useful filters/search:

- `programs`: `is_published`, `search`, `ordering`
- `agenda-cards`: `is_active`, `urgency_tag`, `recommendation_tag`, `category_tag`, `scope_tag`, `pricing_tag`, `search`, `ordering`

Business rules:

- Agenda cards max 15

### Career

| Method | Endpoint |
|---|---|
| GET/POST | `/api/v1/admin/career/opportunities/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/career/opportunities/{id}/` |
| GET/POST | `/api/v1/admin/career/resources/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/career/resources/{id}/` |

Useful filters/search:

- `opportunities`: `is_published`, `search`, `ordering`
- `resources`: `is_active`, `ordering`

Business note:

- Frontend public sebaiknya mengonsumsi resource link dari endpoint `GET /api/v1/public/career/resources/`
- Payload public menggunakan fixed keys

### Advocacy

| Method | Endpoint |
|---|---|
| GET/POST | `/api/v1/admin/advocacy/campaigns/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/advocacy/campaigns/{id}/` |

Useful filters/search:

- `is_published`
- `search`
- `ordering`

### Aspirations

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/v1/admin/aspirations/submissions/` | Paginated list |
| GET | `/api/v1/admin/aspirations/submissions/{id}/` | Detail |
| PATCH | `/api/v1/admin/aspirations/submissions/{id}/` | Update status/visibility/featured |
| POST | `/api/v1/admin/aspirations/submissions/{id}/set-featured/` | Mark featured |
| POST | `/api/v1/admin/aspirations/submissions/{id}/unset-featured/` | Unset featured |

Supported query params:

- `search`
- `ordering`
- `status`
- `visibility`
- `is_featured`

Admin list item shape:

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

- Featured max 6
- Hanya status `investigating` atau `resolved` yang boleh featured

## Frontend Integration Notes

- Untuk list endpoint, selalu cek apakah `data.items` ada sebelum mengiterasi.
- Untuk singleton endpoint, baca data langsung dari `data`.
- Untuk featured aspirations, `sender_name` bisa `null`.
- Untuk tracking ticket, jangan asumsikan user data sensitif tersedia.
- Untuk media/file preview, handle `null`.
- Untuk endpoint yang memakai embed URL, frontend sebaiknya tetap sanitize/render dengan aman.
- Untuk admin dashboard chart, gunakan `data.charts.daily_visitors_last_30_days`.

## Recommended Frontend Fetch Pattern

Pseudo shape:

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

## Useful Docs

- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`
- Raw OpenAPI schema: `/api/schema/`
