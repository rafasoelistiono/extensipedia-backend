# Extensipedia API Consumption Guide

Dokumen ini dibuat untuk frontend, admin client, dan integrasi operasional yang perlu mengonsumsi API Extensipedia dengan cepat dan konsisten.

Sumber acuan dokumen ini adalah implementasi aktual di `config/api_urls.py`, `views.py`, `serializers.py`, `models.py`, settings DRF, dan OpenAPI schema.

## 1. Quick Start

### Base URL

Local development:

```txt
http://127.0.0.1:8000
```

Production mengikuti domain server:

```txt
https://api.domainanda.com
```

API prefix:

```txt
/api/v1/
```

Base path yang paling sering dipakai:

```txt
Public API: /api/v1/public/
Admin API : /api/v1/admin/
```

### URL penting

| Kebutuhan | URL |
|---|---|
| API root | `/api/v1/` |
| Public health check | `/api/v1/public/core/health/` |
| API checker HTML | `/check-api/` |
| Custom admin dashboard HTML | `/admin/` |
| Django admin bawaan | `/django-admin/` |
| Swagger UI | `/api/schema/swagger-ui/` |
| ReDoc | `/api/schema/redoc/` |
| Raw OpenAPI schema | `/api/schema/` |

### Aturan konsumsi paling penting

- Gunakan trailing slash untuk semua endpoint, misalnya `/api/v1/public/about/hero/`.
- Semua response JSON dibungkus dengan `success`, `message`, dan `data`.
- Endpoint list standar mengembalikan `data.items` dan `data.pagination`.
- Endpoint singleton/detail mengembalikan object langsung di `data`.
- ID resource adalah UUID.
- Datetime memakai ISO 8601.
- Public API tidak butuh token.
- Admin API butuh `Authorization: Bearer <access_token>`, kecuali login dan refresh.
- Untuk upload file, gunakan `multipart/form-data`.

## 2. Response Contract

### Success response

```json
{
  "success": true,
  "message": "Request successful",
  "data": {}
}
```

### Error response

```json
{
  "success": false,
  "message": "Request failed",
  "data": {}
}
```

Contoh validation error:

```json
{
  "success": false,
  "message": "This field is required.",
  "data": {
    "title": [
      "This field is required."
    ]
  }
}
```

Contoh not found ticket:

```json
{
  "success": false,
  "message": "Ticket not found.",
  "data": {
    "detail": "Ticket not found."
  }
}
```

### Paginated list

Semua list dari DRF router memakai bentuk berikut:

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

Query pagination:

| Param | Default | Catatan |
|---|---:|---|
| `page` | `1` | Nomor halaman |
| `page_size` | `10` | Maksimum `100` |

### TypeScript shape

```ts
export type ApiResponse<T> = {
  success: boolean;
  message: string;
  data: T;
};

export type Paginated<T> = {
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

## 3. Authentication Admin

### Login

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

Response:

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

Pakai access token untuk admin endpoint:

```txt
Authorization: Bearer <access_token>
```

### Refresh token

```txt
POST /api/v1/admin/accounts/auth/refresh/
```

Request:

```json
{
  "refresh": "jwt-refresh-token"
}
```

Catatan:

- Access token default aktif selama `JWT_ACCESS_TOKEN_MINUTES`.
- Refresh token default aktif selama `JWT_REFRESH_TOKEN_DAYS`.
- `ROTATE_REFRESH_TOKENS=True`.
- Jika response refresh berisi refresh token baru, ganti refresh token lama di client.

### Logout

```txt
POST /api/v1/admin/accounts/auth/logout/
```

Header:

```txt
Authorization: Bearer <access_token>
```

Request:

```json
{
  "refresh": "jwt-refresh-token"
}
```

Response `data` adalah `null` saat berhasil.

## 4. HTTP Status dan Rate Limit

Status yang perlu ditangani client:

| Status | Arti |
|---:|---|
| `200` | Request sukses |
| `201` | Resource berhasil dibuat |
| `400` | Validasi gagal |
| `401` | Token tidak ada, invalid, atau expired |
| `403` | User tidak punya akses |
| `404` | Resource tidak ditemukan |
| `405` | Method tidak tersedia |
| `429` | Rate limit kena throttle |
| `500` | Error server |

Throttle yang aktif:

| Scope | Rate |
|---|---:|
| Submit aspiration | `2/hour`, `5/day` |
| Upvote/vote aspiration | `10/hour`, `30/day` |
| Ticket tracking | `60/hour` |
| Admin login | `5/min`, `20/hour` |

## 5. Cara Membaca Endpoint List

Endpoint list standar mendukung kombinasi query ini jika field-nya didefinisikan di viewset:

```txt
?page=1&page_size=10&search=keyword&ordering=-created_at
```

Catatan:

- `search` hanya aktif pada endpoint yang punya search fields.
- `ordering` hanya boleh memakai field yang didukung endpoint.
- Prefix `-` pada ordering berarti descending, misalnya `?ordering=-updated_at`.
- Filter boolean biasanya menerima `true`, `false`, `1`, atau `0`.

## 6. Public API

Public API tidak membutuhkan login.

### Public endpoint index

| Area | Method | Endpoint | Shape `data` | Query penting |
|---|---|---|---|---|
| Core | GET | `/api/v1/public/core/health/` | Object | - |
| About | GET | `/api/v1/public/about/hero/` | Object | - |
| About | GET | `/api/v1/public/about/tentang-kami/` | Object | - |
| About | GET | `/api/v1/public/about/cabinet-calendar/` | Object | - |
| About | GET | `/api/v1/public/about/profiles/` | `Paginated<T>` | `page`, `page_size` |
| About | GET | `/api/v1/public/about/profiles/{id}/` | Object | - |
| About | GET | `/api/v1/public/about/leadership/` | `Paginated<T>` | `page`, `page_size`, `search`, `ordering` |
| About | GET | `/api/v1/public/about/leadership/{id}/` | Object | - |
| Academic | GET | `/api/v1/public/academic/services/` | `Paginated<T>` | `page`, `page_size`, `search`, `ordering` |
| Academic | GET | `/api/v1/public/academic/services/{id}/` | Object | - |
| Academic | GET | `/api/v1/public/academic/quick-downloads/` | `Paginated<T>` | `page`, `page_size`, `search`, `ordering` |
| Academic | GET | `/api/v1/public/academic/quick-downloads/{id}/` | Object | - |
| Academic | GET | `/api/v1/public/academic/repository/` | Object grouped by section | - |
| Academic | GET | `/api/v1/public/academic/youtube/` | Object | - |
| Academic | GET | `/api/v1/public/academic/countdown-events/` | `Paginated<T>` | `page`, `page_size`, `search`, `ordering` |
| Academic | GET | `/api/v1/public/academic/countdown-events/{id}/` | Object | - |
| Competency | GET | `/api/v1/public/competency/programs/` | `Paginated<T>` | `page`, `page_size`, `search`, `ordering` |
| Competency | GET | `/api/v1/public/competency/programs/{id}/` | Object | - |
| Competency | GET | `/api/v1/public/competency/agenda-cards/` | `Paginated<T>` | `page`, `page_size`, filters, `search`, `ordering` |
| Competency | GET | `/api/v1/public/competency/agenda-cards/{id}/` | Object | - |
| Competency | GET | `/api/v1/public/competency/winner-slides/` | `Paginated<T>` | `page`, `page_size`, `ordering` |
| Competency | GET | `/api/v1/public/competency/winner-slides/{id}/` | Object | - |
| Career | GET | `/api/v1/public/career/resources/` | Object | - |
| Career | GET | `/api/v1/public/career/opportunities/` | `Paginated<T>` | `page`, `page_size`, `search`, `ordering` |
| Career | GET | `/api/v1/public/career/opportunities/{id}/` | Object | - |
| Advocacy | GET | `/api/v1/public/advocacy/campaigns/` | `Paginated<T>` | `page`, `page_size`, `search`, `ordering` |
| Advocacy | GET | `/api/v1/public/advocacy/campaigns/{id}/` | Object | - |
| Aspirations | POST | `/api/v1/public/aspirations/submit/` | Object | `multipart/form-data` |
| Aspirations | GET | `/api/v1/public/aspirations/featured/` | Array | `visibility` |
| Aspirations | POST | `/api/v1/public/aspirations/{id}/upvote/` | Object | - |
| Aspirations | POST | `/api/v1/public/aspirations/{id}/vote/` | Object | - |
| Tickets | GET | `/api/v1/public/tickets/track/` | Object | `ticket_id` |
| Analytics | GET | `/api/v1/public/analytics-dashboard/` | Object | - |

### Public filters and ordering

| Endpoint | Search fields | Ordering fields | Extra filters |
|---|---|---|---|
| `/about/leadership/` | `name`, `role`, `bio` | `display_order`, `name`, `created_at` | - |
| `/academic/services/` | `title`, `description`, `slug` | `title`, `published_at`, `created_at` | - |
| `/academic/quick-downloads/` | `title` | `display_order`, `title`, `created_at` | - |
| `/academic/countdown-events/` | `title` | `display_order`, `target_datetime`, `title` | - |
| `/competency/programs/` | `title`, `description`, `slug` | `title`, `starts_at`, `ends_at`, `created_at` | - |
| `/competency/agenda-cards/` | `title`, `short_description`, `category_tag`, `scope_tag`, `pricing_tag` | `created_at`, `updated_at`, `deadline_date`, `title` | `urgency_tag`, `recommendation_tag`, `category_tag`, `scope_tag`, `pricing_tag` |
| `/competency/winner-slides/` | - | `display_order`, `updated_at`, `created_at` | - |
| `/career/opportunities/` | `title`, `organization`, `description` | `title`, `organization`, `closes_at`, `created_at` | - |
| `/advocacy/campaigns/` | `title`, `summary`, `content`, `slug` | `title`, `created_at`, `updated_at` | - |

Public agenda filters:

```txt
urgency_tag=true|false|1|0
recommendation_tag=true|false|1|0
category_tag=workshop|lomba
scope_tag=nasional|internasional
pricing_tag=berbayar|tidak berbayar
```

Featured aspiration filter:

```txt
visibility=public|anonymous
```

## 7. Public Payload Reference

Bagian ini berisi field yang dipakai frontend public. Field file/image bisa `null`; client harus aman terhadap nilai kosong.

### Core health

```json
{
  "status": "ok"
}
```

### About

`hero`:

```txt
id, title, subtitle, description, image,
primary_button_label, primary_button_url,
secondary_button_label, secondary_button_url
```

`tentang-kami`:

```txt
id, title, subtitle, description, image
```

`cabinet-calendar`:

```txt
id, title, description, embed_url, embed_code, provider
```

Catatan:

- `embed_url` public berasal dari `sanitized_embed_url`.
- `provider` bisa `google_calendar`, `youtube`, `vimeo`, `google`, atau `external`.
- `AboutSection` punya endpoint public, tetapi belum punya admin API khusus.

`profiles`:

```txt
id, name, tagline, summary, vision, mission,
logo, contact_email, contact_phone, address
```

`leadership`:

```txt
id, name, role, bio, photo, display_order
```

### Academic

`services`:

```txt
id, title, slug, description, thumbnail, published_at
```

`quick-downloads`:

```txt
id, title, resource_type, resource_url, display_order
```

Catatan:

- `resource_type` adalah `file` atau `external_link`.
- `resource_url` bisa absolute URL untuk file upload atau URL eksternal.

`repository`:

```json
{
  "akuntansi": [
    {
      "id": "uuid",
      "title": "Materi Akuntansi",
      "google_drive_link": "https://drive.google.com/...",
      "display_order": 1
    }
  ],
  "manajemen": []
}
```

Catatan:

- Repository tidak dipaginasi.
- Section yang tersedia hanya `akuntansi` dan `manajemen`.

`youtube`:

```txt
id, title, description, embed_url
```

`countdown-events`:

```txt
id, title, target_datetime, display_order
```

### Competency

`programs`:

```txt
id, title, slug, description, poster, starts_at, ends_at
```

`agenda-cards`:

```txt
id, title, short_description, urgency_tag, recommendation_tag,
category_tag, scope_tag, pricing_tag, deadline_date,
registration_link, google_calendar_link, countdown_days
```

Catatan:

- `countdown_days` dihitung backend dari `deadline_date`.
- `category_tag`: `workshop` atau `lomba`.
- `scope_tag`: `nasional` atau `internasional`.
- `pricing_tag`: `berbayar` atau `tidak berbayar`.
- Default ordering: `-created_at,-updated_at,deadline_date,title`.

`winner-slides`:

```txt
id, image_url, alt_text, display_order, updated_at
```

Catatan:

- Public hanya menampilkan slot yang sudah punya gambar.
- Slot tetap berjumlah maksimum `5`.

### Career

`resources`:

```txt
id, cv_templates, cover_letter, portfolio_guide,
salary_script, case_study_interview_prep
```

`opportunities`:

```txt
id, title, organization, description, apply_url, closes_at
```

### Advocacy

`campaigns`:

```txt
id, title, slug, summary, content, banner, embed_url
```

### Aspirations

Submit aspiration:

```txt
POST /api/v1/public/aspirations/submit/
Content-Type: multipart/form-data
```

Required fields:

```txt
full_name, npm, email, title, short_description
```

Optional fields:

```txt
evidence_attachment
```

Catatan submit:

- `evidence_attachment` hanya menerima image atau PDF.
- Public client tidak bisa memilih `visibility`.
- Record baru dibuat dengan `visibility=anonymous`.
- Status awal adalah `submitted`.
- `ticket_id` otomatis dibuat dengan format `ASP-XXXXXXXXXX`.
- Email konfirmasi dikirim secara sinkron setelah data tersimpan.

Response submit:

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

Featured aspirations:

```txt
id, ticket_id, title, short_description, visibility,
sender_name, status, upvote_count, vote_count, created_at
```

Catatan featured:

- Tidak dipaginasi.
- Maksimum `6` item.
- Hanya `is_featured=true`.
- Hanya status `investigating` atau `resolved`.
- `sender_name` bernilai `null` jika `visibility=anonymous`.

Upvote/vote response:

```json
{
  "id": "uuid",
  "ticket_id": "ASP-1A2B3C4D5E",
  "upvote_count": 13,
  "vote_count": 7
}
```

Tracking ticket:

```txt
GET /api/v1/public/tickets/track/?ticket_id=ASP-1A2B3C4D5E
```

Response fields:

```txt
ticket_id, title, status, submitted_at, updated_at,
visibility, short_description
```

Jika `ticket_id` kosong, backend mengembalikan object kosong yang aman:

```json
{
  "ticket_id": null,
  "title": null,
  "status": null,
  "submitted_at": null,
  "updated_at": null,
  "visibility": null,
  "short_description": null
}
```

Tracking tidak pernah mengekspos `full_name`, `npm`, atau `email`.

### Analytics public

```json
{
  "available": false
}
```

Analytics dashboard penuh hanya tersedia dari Admin API.

## 8. Admin API

Semua admin endpoint membutuhkan Bearer token kecuali:

```txt
POST /api/v1/admin/accounts/auth/login/
POST /api/v1/admin/accounts/auth/refresh/
```

Admin API memakai serializer admin. Sebagian besar endpoint CRUD admin mengekspos semua field model ditambah audit fields:

```txt
id, created_at, updated_at, created_by, updated_by
```

Gunakan Swagger/ReDoc untuk melihat required field lengkap saat membuat form admin.

### Admin endpoint index

| Area | Method | Endpoint | Catatan |
|---|---|---|---|
| Accounts | POST | `/api/v1/admin/accounts/auth/login/` | Login admin |
| Accounts | POST | `/api/v1/admin/accounts/auth/refresh/` | Refresh JWT |
| Accounts | POST | `/api/v1/admin/accounts/auth/logout/` | Blacklist refresh token |
| Accounts | GET | `/api/v1/admin/accounts/profile/` | Current admin profile |
| Accounts | GET/POST | `/api/v1/admin/accounts/users/` | Superadmin only |
| Accounts | GET/PUT/PATCH/DELETE | `/api/v1/admin/accounts/users/{id}/` | Superadmin only |
| Dashboard | GET | `/api/v1/admin/dashboard/summary/` | Cards dan chart |
| Dashboard | GET | `/api/v1/admin/dashboard/ticket-log/` | 20 log tiket terbaru |
| About | GET/POST | `/api/v1/admin/about/profiles/` | CRUD profile organisasi |
| About | GET/PUT/PATCH/DELETE | `/api/v1/admin/about/profiles/{id}/` | CRUD profile organisasi |
| About | GET/POST | `/api/v1/admin/about/leadership/` | CRUD leadership |
| About | GET/PUT/PATCH/DELETE | `/api/v1/admin/about/leadership/{id}/` | CRUD leadership |
| About | GET/POST | `/api/v1/admin/about/heroes/` | CRUD hero |
| About | GET/PUT/PATCH/DELETE | `/api/v1/admin/about/heroes/{id}/` | CRUD hero |
| About | GET | `/api/v1/admin/about/cabinet-calendar/` | Singleton |
| About | PUT/PATCH | `/api/v1/admin/about/cabinet-calendar/` | Create/update singleton |
| Academic | GET/POST | `/api/v1/admin/academic/services/` | CRUD academic service |
| Academic | GET/PUT/PATCH/DELETE | `/api/v1/admin/academic/services/{id}/` | CRUD academic service |
| Academic | GET/POST | `/api/v1/admin/academic/quick-downloads/` | CRUD quick download |
| Academic | GET/PUT/PATCH/DELETE | `/api/v1/admin/academic/quick-downloads/{id}/` | CRUD quick download |
| Academic | GET/POST | `/api/v1/admin/academic/repository-materials/` | CRUD repository material |
| Academic | GET/PUT/PATCH/DELETE | `/api/v1/admin/academic/repository-materials/{id}/` | CRUD repository material |
| Academic | GET/POST | `/api/v1/admin/academic/youtube-sections/` | CRUD YouTube section |
| Academic | GET/PUT/PATCH/DELETE | `/api/v1/admin/academic/youtube-sections/{id}/` | CRUD YouTube section |
| Academic | GET/POST | `/api/v1/admin/academic/countdown-events/` | CRUD countdown event |
| Academic | GET/PUT/PATCH/DELETE | `/api/v1/admin/academic/countdown-events/{id}/` | CRUD countdown event |
| Competency | GET/POST | `/api/v1/admin/competency/programs/` | CRUD program |
| Competency | GET/PUT/PATCH/DELETE | `/api/v1/admin/competency/programs/{id}/` | CRUD program |
| Competency | GET/POST | `/api/v1/admin/competency/agenda-cards/` | CRUD agenda card |
| Competency | GET/PUT/PATCH/DELETE | `/api/v1/admin/competency/agenda-cards/{id}/` | CRUD agenda card |
| Competency | GET | `/api/v1/admin/competency/winner-slides/` | Slot tetap |
| Competency | GET/PATCH | `/api/v1/admin/competency/winner-slides/{id}/` | Update image/alt text |
| Career | GET/POST | `/api/v1/admin/career/opportunities/` | CRUD opportunity |
| Career | GET/PUT/PATCH/DELETE | `/api/v1/admin/career/opportunities/{id}/` | CRUD opportunity |
| Career | GET/POST | `/api/v1/admin/career/resources/` | CRUD resource config |
| Career | GET/PUT/PATCH/DELETE | `/api/v1/admin/career/resources/{id}/` | CRUD resource config |
| Advocacy | GET/POST | `/api/v1/admin/advocacy/campaigns/` | CRUD campaign |
| Advocacy | GET/PUT/PATCH/DELETE | `/api/v1/admin/advocacy/campaigns/{id}/` | CRUD campaign |
| Aspirations | GET/POST | `/api/v1/admin/aspirations/submissions/` | List/create submission |
| Aspirations | GET/PATCH | `/api/v1/admin/aspirations/submissions/{id}/` | Detail/update submission |
| Aspirations | POST | `/api/v1/admin/aspirations/submissions/{id}/set-featured/` | Mark featured |
| Aspirations | POST | `/api/v1/admin/aspirations/submissions/{id}/unset-featured/` | Remove featured |

### Admin filters, search, and ordering

| Endpoint | Filters | Search fields | Ordering fields |
|---|---|---|---|
| `/accounts/users/` | `is_active`, `is_staff`, `is_superuser` | `email`, `full_name` | `full_name`, `email`, `created_at`, `updated_at` |
| `/about/profiles/` | `is_active` | `name`, `tagline`, `summary`, `contact_email` | `name`, `created_at`, `updated_at` |
| `/about/leadership/` | `is_active` | `name`, `role`, `bio` | `display_order`, `name`, `created_at`, `updated_at` |
| `/about/heroes/` | `is_active` | `title`, `subtitle`, `description` | `updated_at`, `created_at`, `title` |
| `/academic/services/` | `is_published` | `title`, `description`, `slug` | `title`, `published_at`, `created_at`, `updated_at` |
| `/academic/quick-downloads/` | `is_active` | `title` | `display_order`, `title`, `created_at`, `updated_at` |
| `/academic/repository-materials/` | `section` | `title`, `google_drive_link` | `section`, `display_order`, `title`, `created_at` |
| `/academic/youtube-sections/` | `is_active` | `title`, `description` | `updated_at`, `created_at`, `title` |
| `/academic/countdown-events/` | `is_active` | `title` | `display_order`, `target_datetime`, `created_at`, `updated_at` |
| `/competency/programs/` | `is_published` | `title`, `description`, `slug` | `title`, `starts_at`, `ends_at`, `created_at`, `updated_at` |
| `/competency/agenda-cards/` | `is_active`, `urgency_tag`, `recommendation_tag`, `category_tag`, `scope_tag`, `pricing_tag` | `title`, `short_description`, `category_tag`, `scope_tag`, `pricing_tag` | `deadline_date`, `created_at`, `updated_at`, `title` |
| `/competency/winner-slides/` | `display_order` | `alt_text` | `display_order`, `created_at`, `updated_at` |
| `/career/opportunities/` | `is_published` | `title`, `organization`, `description` | `title`, `organization`, `closes_at`, `created_at`, `updated_at` |
| `/career/resources/` | `is_active` | - | `updated_at`, `created_at` |
| `/advocacy/campaigns/` | `is_published` | `title`, `summary`, `content`, `slug` | `title`, `created_at`, `updated_at` |
| `/aspirations/submissions/` | `status`, `visibility`, `is_featured` | `ticket_id`, `title`, `full_name`, `email`, `npm` | `created_at`, `updated_at`, `status`, `ticket_id`, `is_featured` |

### Dashboard payload

`GET /api/v1/admin/dashboard/summary/`:

```txt
cards.total_aspiration_submissions
cards.status_counts.submitted
cards.status_counts.investigating
cards.status_counts.resolved
cards.total_featured_aspirations
cards.total_visitors_last_30_days
charts.daily_visitors_last_30_days[]
```

`GET /api/v1/admin/dashboard/ticket-log/`:

```txt
id, ticket_id, title, action, message, actor_name,
status_snapshot, visibility_snapshot, metadata, created_at
```

Ticket log tidak dipaginasi; backend mengambil 20 log terbaru.

### Admin business rules

Accounts:

- `/admin/accounts/users/` hanya bisa diakses superadmin.
- `role=admin` menghasilkan `is_staff=true`, `is_superuser=false`.
- `role=superadmin` menghasilkan `is_staff=true`, `is_superuser=true`.
- `password` optional saat create; jika kosong, user dibuat dengan unusable password.

About:

- `hero` adalah single-active configuration.
- `cabinet-calendar` adalah singleton dan hanya memakai `GET`, `PUT`, `PATCH`.
- `cabinet-calendar.embed_url` public memakai versi sanitasi.
- `AboutSection` belum memiliki Admin API khusus, walaupun public endpoint tersedia.

Academic:

- Quick downloads maksimum `5` item total.
- Quick download harus memilih tepat salah satu: upload `file` atau `external_url`.
- Repository material hanya mendukung section `akuntansi` dan `manajemen`.
- Setiap section repository maksimum `3` item.
- YouTube section adalah single-active configuration.
- Embed URL/code divalidasi dan disanitasi.

Competency:

- Agenda cards maksimum `15` record.
- `short_description` agenda card maksimum `300` karakter.
- `category_tag`: `workshop` atau `lomba`.
- `scope_tag`: `nasional` atau `internasional`.
- `pricing_tag`: `berbayar` atau `tidak berbayar`.
- Winner slide memakai `5` slot tetap.
- Admin winner slide hanya mengizinkan `GET` dan `PATCH`.
- Public winner slide hanya menampilkan slot yang sudah punya gambar.

Career:

- Career resources adalah single-active configuration.
- Public `/career/resources/` mengambil konfigurasi aktif.

Advocacy:

- Campaign public hanya menampilkan record `is_published=true`.
- Dashboard HTML belum menyediakan semua pengelolaan campaign, tetapi Admin API tersedia.

Aspirations:

- Featured maksimum `6`.
- Hanya status `investigating` atau `resolved` yang bisa dijadikan featured.
- `ticket_id`, `upvote_count`, dan `vote_count` read-only.
- Perubahan penting menulis `AspirationActivityLog`.
- Admin detail mengekspos data sensitif submitter seperti `full_name`, `npm`, dan `email`; jangan gunakan endpoint admin di frontend public.

## 9. Frontend Recipes

### Fetch helper minimal

```ts
const API_BASE_URL = "http://127.0.0.1:8000";

type ApiResponse<T> = {
  success: boolean;
  message: string;
  data: T;
};

export async function apiFetch<T>(
  path: string,
  options: RequestInit & { accessToken?: string } = {},
): Promise<ApiResponse<T>> {
  const headers = new Headers(options.headers);
  const body = options.body;

  if (!(body instanceof FormData) && body !== undefined && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (options.accessToken) {
    headers.set("Authorization", `Bearer ${options.accessToken}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const payload = (await response.json()) as ApiResponse<T>;

  if (!response.ok || !payload.success) {
    throw new Error(payload.message || `Request failed with status ${response.status}`);
  }

  return payload;
}
```

### Ambil paginated public list

```ts
type AcademicService = {
  id: string;
  title: string;
  slug: string;
  description: string;
  thumbnail: string | null;
  published_at: string | null;
};

const response = await apiFetch<Paginated<AcademicService>>(
  "/api/v1/public/academic/services/?page=1&page_size=6&ordering=title",
);

const services = response.data.items;
const pagination = response.data.pagination;
```

### Ambil singleton public

```ts
type HeroSection = {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  image: string | null;
  primary_button_label: string;
  primary_button_url: string;
  secondary_button_label: string;
  secondary_button_url: string;
};

const response = await apiFetch<HeroSection>("/api/v1/public/about/hero/");
const hero = response.data;
```

### Submit aspiration dengan file

```ts
const formData = new FormData();
formData.set("full_name", fullName);
formData.set("npm", npm);
formData.set("email", email);
formData.set("title", title);
formData.set("short_description", shortDescription);

if (file) {
  formData.set("evidence_attachment", file);
}

const response = await apiFetch<{
  ticket_id: string;
  title: string;
  status: string;
  submitted_at: string;
  updated_at: string;
  visibility: "anonymous" | "public";
  short_description: string;
}>("/api/v1/public/aspirations/submit/", {
  method: "POST",
  body: formData,
});
```

### Login dan panggil admin endpoint

```ts
const login = await apiFetch<{
  refresh: string;
  access: string;
  user: {
    id: string;
    email: string;
    full_name: string;
    role: "admin" | "superadmin";
  };
}>("/api/v1/admin/accounts/auth/login/", {
  method: "POST",
  body: JSON.stringify({
    email,
    password,
  }),
});

const summary = await apiFetch<unknown>("/api/v1/admin/dashboard/summary/", {
  accessToken: login.data.access,
});
```

### Refresh token

```ts
const refreshed = await apiFetch<{
  access: string;
  refresh?: string;
}>("/api/v1/admin/accounts/auth/refresh/", {
  method: "POST",
  body: JSON.stringify({
    refresh: currentRefreshToken,
  }),
});

const nextAccessToken = refreshed.data.access;
const nextRefreshToken = refreshed.data.refresh ?? currentRefreshToken;
```

## 10. Operational Notes

Deployment:

- Production sebaiknya memakai `DJANGO_SETTINGS_MODULE=config.settings.prod` jika file production setting tersedia di environment deployment.
- `DATABASE_URL` harus mengarah ke PostgreSQL.
- `DJANGO_ALLOWED_HOSTS`, `DJANGO_CORS_ALLOWED_ORIGINS`, dan `DJANGO_CSRF_TRUSTED_ORIGINS` harus sesuai domain production.
- Static file dilayani WhiteNoise setelah `collectstatic`.
- Media file perlu dilayani reverse proxy seperti Nginx.

Email:

- Submit aspiration mengirim email konfirmasi secara sinkron.
- Jika SMTP production salah, data bisa sudah tersimpan tetapi response ke client gagal karena email error.
- Untuk UX public, tampilkan error umum dan sediakan opsi retry/check ticket jika dibutuhkan.

Analytics:

- Visitor analytics public hanya menghitung `GET` dan `HEAD` di bawah `/api/v1/public/`.
- Endpoint `/api/v1/public/tickets/` tidak dihitung.
- Deduplikasi visitor memakai cache process-local.
- Pada deployment multi-worker, gunakan cache terpusat seperti Redis jika butuh angka visitor yang lebih stabil.

Security:

- Jangan gunakan Admin API di frontend public.
- Jangan render `embed_code` tanpa sanitasi sisi frontend.
- Jangan asumsi semua file/image selalu ada; handle `null`.
- Tangani `401` dengan refresh token.
- Tangani `429` dengan pesan retry/backoff.

## 11. Known Gaps

- Prefix `/api/v1/public/accounts/` ada di routing, tetapi belum memiliki endpoint aktif.
- `AboutSection` punya endpoint public `/api/v1/public/about/tentang-kami/`, tetapi belum ada Admin API khusus.
- Dashboard HTML `/admin/` belum mencakup seluruh resource yang tersedia di Admin API.
- Beberapa endpoint custom tidak dipaginasi: repository, YouTube singleton, career resources, featured aspirations, ticket tracking, dashboard summary, dan ticket log.
