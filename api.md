# API Guide for Frontend and Deployment Context

Dokumen ini merangkum API yang aktif di codebase saat ini dan beberapa catatan analisis yang penting untuk frontend, integrasi admin, dan operasional deployment.

Dokumen ini disusun dari implementasi aktual pada `config/api_urls.py`, `views.py`, `serializers.py`, `models.py`, dan settings production.

## 1. Gambaran Aplikasi

### Stack utama

- Django 6
- Django REST Framework
- SimpleJWT untuk auth admin API
- drf-spectacular untuk OpenAPI schema
- WhiteNoise untuk static files
- PostgreSQL sebagai database utama
- custom admin dashboard template-based di `/admin/`

### Peta URL utama

- Checker API: `/check-api/`
- Custom admin dashboard: `/admin/`
- Django admin bawaan: `/django-admin/`
- API root: `/api/v1/`
- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`

### Pembagian interface

- Public site mengambil data dari `/api/v1/public/...`
- Admin SPA atau client admin dapat memakai `/api/v1/admin/...`
- Tim operasional juga bisa memakai dashboard HTML bawaan di `/admin/`

### Temuan analisis penting

- Response API dibungkus konsisten dengan format `success`, `message`, `data`
- Sebagian besar endpoint list memakai pagination standar DRF yang dibungkus sebagai `data.items` dan `data.pagination`
- Beberapa endpoint bersifat singleton dan mengembalikan object langsung di `data`
- Ada resource public yang belum punya admin API khusus, terutama `AboutSection`
- Dashboard HTML `/admin/` belum mencakup seluruh admin API; beberapa resource hanya tersedia lewat API admin
- Submit aspiration mengirim email sinkron. Jika SMTP production salah, tiket bisa sudah tersimpan tetapi request tetap gagal ke client
- Visitor analytics public memakai cache process-local. Pada deployment multi-worker, deduplikasi visitor tidak akan seakurat cache terpusat seperti Redis

## 2. Base URL

Local development:

```txt
http://127.0.0.1:8000
```

Base URL production mengikuti domain atau IP server Anda, misalnya:

```txt
https://api.domainanda.com
```

Prefix seluruh endpoint API:

```txt
/api/v1/
```

Pembagian scope:

- Public API: `/api/v1/public/...`
- Admin API: `/api/v1/admin/...`

API root:

```txt
GET /api/v1/
```

Response API root:

```json
{
  "success": true,
  "message": "Extensipedia API v1",
  "data": {
    "name": "Extensipedia API",
    "version": "v1",
    "public_base_url": "http://127.0.0.1:8000/api/v1/public/",
    "admin_base_url": "http://127.0.0.1:8000/api/v1/admin/"
  }
}
```

## 3. Global Response Format

Semua response sukses memakai bentuk:

```json
{
  "success": true,
  "message": "Request successful",
  "data": {}
}
```

Semua response error dibungkus menjadi:

```json
{
  "success": false,
  "message": "Request failed",
  "data": {}
}
```

Contoh error tracking ticket:

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

Endpoint list yang dipaginasi mengembalikan bentuk:

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

- `page_size` maksimum adalah `100`
- endpoint singleton tidak memakai `data.items`
- beberapa endpoint custom mengembalikan array langsung di `data`

## 5. Authentication

### Public API

- tidak membutuhkan login

### Admin API

- menggunakan JWT Bearer token
- endpoint login:

```txt
POST /api/v1/admin/accounts/auth/login/
```

Request body login:

```json
{
  "email": "admin@example.com",
  "password": "your-password"
}
```

Contoh response login:

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

Catatan refresh:

- `ROTATE_REFRESH_TOKENS=True`
- backend dapat mengembalikan refresh token baru setelah refresh

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

## 6. Global Behavior dan Constraint

- Trailing slash adalah format standar yang sebaiknya selalu dipakai client
- Untuk aspiration submit, backend juga menerima `/submit` tanpa slash, tetapi client tetap sebaiknya memakai `/submit/`
- Endpoint vote dan upvote juga menerima bentuk tanpa trailing slash
- File media biasanya dikembalikan sebagai absolute URL jika request berjalan normal melalui DRF serializer context
- Frontend tetap sebaiknya aman terhadap `null` pada field file/image/embed
- Public analytics hanya menghitung `GET` dan `HEAD` di bawah `/api/v1/public/`, selain endpoint tracking tiket

Throttle rate penting:

- aspiration submit: `2/hour`, `5/day`
- aspiration interaction: `10/hour`, `30/day`
- ticket tracking: `60/hour`
- admin login: `5/min`, `20/hour`

## 7. Public API

### 7.1 Core

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | `/api/v1/public/core/health/` | Health check backend |

Contoh response:

```json
{
  "success": true,
  "message": "Service is healthy",
  "data": {
    "status": "ok"
  }
}
```

### 7.2 About

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | `/api/v1/public/about/hero/` | Hero aktif |
| GET | `/api/v1/public/about/tentang-kami/` | About section aktif |
| GET | `/api/v1/public/about/cabinet-calendar/` | Cabinet calendar aktif |
| GET | `/api/v1/public/about/profiles/` | List organization profile aktif |
| GET | `/api/v1/public/about/profiles/{id}/` | Detail organization profile |
| GET | `/api/v1/public/about/leadership/` | List leadership aktif |
| GET | `/api/v1/public/about/leadership/{id}/` | Detail leadership |

Field penting:

- `hero`: `title`, `subtitle`, `description`, `image`, `primary_button_label`, `primary_button_url`, `secondary_button_label`, `secondary_button_url`
- `tentang-kami`: `title`, `subtitle`, `description`, `image`
- `cabinet-calendar`: `title`, `description`, `embed_url`, `embed_code`, `provider`
- `profiles`: `name`, `tagline`, `summary`, `vision`, `mission`, `logo`, `contact_email`, `contact_phone`, `address`
- `leadership`: `name`, `role`, `bio`, `photo`, `display_order`

Catatan:

- `cabinet-calendar` adalah singleton
- `embed_url` public adalah hasil sanitasi dari `sanitized_embed_url`
- `leadership` mendukung `search` dan `ordering`
- `AboutSection` saat ini ada endpoint public tetapi tidak ada admin API khusus untuk mengubahnya

### 7.3 Academic

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | `/api/v1/public/academic/services/` | List layanan akademik publish |
| GET | `/api/v1/public/academic/services/{id}/` | Detail layanan akademik |
| GET | `/api/v1/public/academic/quick-downloads/` | List quick downloads aktif |
| GET | `/api/v1/public/academic/quick-downloads/{id}/` | Detail quick download |
| GET | `/api/v1/public/academic/repository/` | Object grouped repository |
| GET | `/api/v1/public/academic/youtube/` | YouTube section aktif |
| GET | `/api/v1/public/academic/countdown-events/` | List countdown event aktif |
| GET | `/api/v1/public/academic/countdown-events/{id}/` | Detail countdown event |

Field penting:

- `services`: `title`, `slug`, `description`, `thumbnail`, `published_at`
- `quick-downloads`: `title`, `resource_type`, `resource_url`, `display_order`
- `repository`: object dengan key `akuntansi` dan `manajemen`
- `youtube`: `title`, `description`, `embed_url`
- `countdown-events`: `title`, `target_datetime`, `display_order`

Catatan:

- `quick-downloads.resource_type` bernilai `file` atau `external_link`
- `repository` tidak dipaginasi
- repository hanya mendukung section `akuntansi` dan `manajemen`
- `countdown-events` mendukung `search` dan `ordering`

### 7.4 Competency

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | `/api/v1/public/competency/programs/` | List program kompetensi publish |
| GET | `/api/v1/public/competency/programs/{id}/` | Detail program kompetensi |
| GET | `/api/v1/public/competency/agenda-cards/` | List agenda card aktif |
| GET | `/api/v1/public/competency/agenda-cards/{id}/` | Detail agenda card |
| GET | `/api/v1/public/competency/winner-slides/` | List winner slide yang sudah berisi gambar |
| GET | `/api/v1/public/competency/winner-slides/{id}/` | Detail winner slide |

Filter penting `agenda-cards`:

- `urgency_tag=true|false|1|0`
- `recommendation_tag=true|false|1|0`
- `category_tag=workshop|lomba`
- `scope_tag=nasional|internasional`
- `pricing_tag=berbayar|tidak berbayar`
- `search`
- `ordering`

Field penting:

- `programs`: `title`, `slug`, `description`, `poster`, `starts_at`, `ends_at`
- `agenda-cards`: `title`, `short_description`, `urgency_tag`, `recommendation_tag`, `category_tag`, `scope_tag`, `pricing_tag`, `deadline_date`, `registration_link`, `google_calendar_link`, `countdown_days`
- `winner-slides`: `image_url`, `alt_text`, `display_order`, `updated_at`

Catatan:

- `countdown_days` dihitung backend dari `deadline_date`
- public winner slide hanya menampilkan slot yang sudah punya gambar
- urutan default agenda card adalah `-created_at,-updated_at,deadline_date,title`

### 7.5 Career

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | `/api/v1/public/career/resources/` | Resource karier aktif |
| GET | `/api/v1/public/career/opportunities/` | List career opportunity publish |
| GET | `/api/v1/public/career/opportunities/{id}/` | Detail opportunity |

Field penting:

- `resources`: `cv_templates`, `cover_letter`, `portfolio_guide`, `salary_script`, `case_study_interview_prep`
- `opportunities`: `title`, `organization`, `description`, `apply_url`, `closes_at`

Catatan:

- public resources mengambil record yang aktif
- model resources bersifat single active configuration

### 7.6 Advocacy

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | `/api/v1/public/advocacy/campaigns/` | List campaign publish |
| GET | `/api/v1/public/advocacy/campaigns/{id}/` | Detail campaign |

Field penting:

- `title`
- `slug`
- `summary`
- `content`
- `banner`
- `embed_url`

### 7.7 Aspirations

| Method | Endpoint | Kegunaan |
|---|---|---|
| POST | `/api/v1/public/aspirations/submit/` | Submit aspiration baru |
| GET | `/api/v1/public/aspirations/featured/` | List featured aspirations |
| POST | `/api/v1/public/aspirations/{id}/upvote/` | Tambah upvote |
| POST | `/api/v1/public/aspirations/{id}/vote/` | Tambah vote |
| GET | `/api/v1/public/tickets/track/?ticket_id=ASP-XXXXXXXXXX` | Tracking ticket |

Request `submit`:

- content type: `multipart/form-data`
- required fields:
  - `full_name`
  - `npm`
  - `email`
  - `title`
  - `short_description`
- optional:
  - `evidence_attachment`

Catatan submit:

- `visibility` tidak bisa dipilih public client
- record baru akan dibuat dengan `visibility=anonymous`
- `status` awal adalah `submitted`
- `ticket_id` otomatis dibuat format `ASP-XXXXXXXXXX`
- `evidence_attachment` hanya menerima image atau PDF

Query param `featured`:

- `visibility=public`
- `visibility=anonymous`

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

Catatan featured:

- hanya menampilkan aspiration yang `is_featured=true`
- status yang boleh tampil public adalah `investigating` atau `resolved`
- `sender_name` menjadi `null` jika visibility `anonymous`
- result tidak dipaginasi
- maksimum featured public adalah `6`

Contoh response interaction:

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

Catatan tracking:

- jika `ticket_id` kosong, backend mengembalikan object kosong yang aman
- jika format tiket salah atau tiket tidak ditemukan, backend mengembalikan `404`
- tracking tidak pernah mengekspos `full_name`, `npm`, atau `email`

### 7.8 Analytics Info

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | `/api/v1/public/analytics-dashboard/` | Placeholder informasi untuk public |

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

## 8. Admin API

Semua endpoint admin membutuhkan Bearer token, kecuali login dan refresh.

### 8.1 Accounts

| Method | Endpoint | Kegunaan |
|---|---|---|
| POST | `/api/v1/admin/accounts/auth/login/` | Login |
| POST | `/api/v1/admin/accounts/auth/refresh/` | Refresh token |
| POST | `/api/v1/admin/accounts/auth/logout/` | Logout |
| GET | `/api/v1/admin/accounts/profile/` | Current admin profile |
| GET/POST | `/api/v1/admin/accounts/users/` | List dan create user admin |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/accounts/users/{id}/` | Detail dan kelola user admin |

Filter/search users:

- `is_active`
- `is_staff`
- `is_superuser`
- `search`
- `ordering`

Catatan:

- endpoint `users` hanya bisa diakses superadmin
- field `role` tersedia sebagai `admin` atau `superadmin`
- saat create/update user, `role` akan menentukan kombinasi `is_staff` dan `is_superuser`

### 8.2 Dashboard

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | `/api/v1/admin/dashboard/summary/` | Summary cards dan chart visitor |
| GET | `/api/v1/admin/dashboard/ticket-log/` | 20 log aktivitas tiket terbaru |

Field summary:

- `cards.total_aspiration_submissions`
- `cards.status_counts.submitted`
- `cards.status_counts.investigating`
- `cards.status_counts.resolved`
- `cards.total_featured_aspirations`
- `cards.total_visitors_last_30_days`
- `charts.daily_visitors_last_30_days[]`

Field ticket log:

- `ticket_id`
- `title`
- `action`
- `message`
- `actor_name`
- `status_snapshot`
- `visibility_snapshot`
- `metadata`
- `created_at`

### 8.3 About

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
- `hero` adalah single-active configuration
- `AboutSection` belum memiliki admin API tersendiri walaupun endpoint public-nya ada

### 8.4 Academic

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

- quick downloads maksimum `5` item total
- setiap repository section maksimum `3` item
- quick download harus tepat salah satu: upload file atau external URL
- repository material hanya untuk section `akuntansi` dan `manajemen`
- YouTube section adalah single-active configuration

### 8.5 Competency

| Method | Endpoint |
|---|---|
| GET/POST | `/api/v1/admin/competency/programs/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/competency/programs/{id}/` |
| GET/POST | `/api/v1/admin/competency/agenda-cards/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/competency/agenda-cards/{id}/` |
| GET | `/api/v1/admin/competency/winner-slides/` |
| GET/PATCH | `/api/v1/admin/competency/winner-slides/{id}/` |

Filter/search:

- `programs`: `is_published`, `search`, `ordering`
- `agenda-cards`: `is_active`, `urgency_tag`, `recommendation_tag`, `category_tag`, `scope_tag`, `pricing_tag`, `search`, `ordering`
- `winner-slides`: `display_order`, `search`, `ordering`

Business rules:

- agenda cards maksimum `15`
- `category_tag`: `workshop` atau `lomba`
- `scope_tag`: `nasional` atau `internasional`
- `pricing_tag`: `berbayar` atau `tidak berbayar`
- winner slide memakai `5` slot tetap
- admin API winner slide hanya mengizinkan `GET` dan `PATCH`

### 8.6 Career

| Method | Endpoint |
|---|---|
| GET/POST | `/api/v1/admin/career/opportunities/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/career/opportunities/{id}/` |
| GET/POST | `/api/v1/admin/career/resources/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/career/resources/{id}/` |

Filter/search:

- `opportunities`: `is_published`, `search`, `ordering`
- `resources`: `is_active`, `ordering`

Catatan:

- `resources` adalah single-active configuration
- dashboard HTML saat ini fokus mengelola resource links, bukan opportunity list

### 8.7 Advocacy

| Method | Endpoint |
|---|---|
| GET/POST | `/api/v1/admin/advocacy/campaigns/` |
| GET/PUT/PATCH/DELETE | `/api/v1/admin/advocacy/campaigns/{id}/` |

Filter/search:

- `is_published`
- `search`
- `ordering`

Catatan:

- custom dashboard HTML belum menyediakan halaman pengelolaan campaign, tetapi admin API tersedia

### 8.8 Aspirations

| Method | Endpoint | Kegunaan |
|---|---|---|
| GET | `/api/v1/admin/aspirations/submissions/` | List submission |
| GET | `/api/v1/admin/aspirations/submissions/{id}/` | Detail submission |
| PATCH | `/api/v1/admin/aspirations/submissions/{id}/` | Update submission |
| POST | `/api/v1/admin/aspirations/submissions/{id}/set-featured/` | Set featured |
| POST | `/api/v1/admin/aspirations/submissions/{id}/unset-featured/` | Unset featured |

Filter/search:

- `status`
- `visibility`
- `is_featured`
- `search`
- `ordering`

Field admin detail:

- seluruh field model tersedia, termasuk `full_name`, `npm`, `email`, `evidence_attachment`, `ticket_id`, `status`, `visibility`, `is_featured`, `upvote_count`, `vote_count`

Business rules:

- featured maksimum `6`
- hanya `investigating` atau `resolved` yang boleh menjadi featured
- `ticket_id`, `upvote_count`, dan `vote_count` tidak editable dari admin serializer
- setiap perubahan penting akan menulis `AspirationActivityLog`

## 9. Catatan Operasional Frontend

- Untuk endpoint list, cek apakah payload berada di `data.items`
- Untuk endpoint singleton, baca object langsung dari `data`
- Jangan asumsi semua list punya bentuk yang sama karena ada endpoint custom seperti `repository`, `featured`, dan `ticket-log`
- Untuk render embed code atau embed URL, tetap lakukan sanitasi frontend yang aman
- Untuk file upload aspiration, gunakan `multipart/form-data`
- Frontend sebaiknya menangani `429 Too Many Requests`
- Frontend admin sebaiknya meng-handle `401`, `403`, dan rotasi refresh token

Contoh type aman:

```ts
type ApiResponse<T> = {
  success: boolean;
  message: string;
  data: T;
};
```

Contoh pagination:

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

## 10. Catatan Operasional Backend

Hal yang perlu diperhatikan saat project ini dijalankan di server:

- Production harus memakai `DJANGO_SETTINGS_MODULE=config.settings.prod`
- `DATABASE_URL` wajib mengarah ke PostgreSQL
- `DJANGO_ALLOWED_HOSTS`, `DJANGO_CORS_ALLOWED_ORIGINS`, dan `DJANGO_CSRF_TRUSTED_ORIGINS` harus sesuai domain production
- Static file bisa dilayani WhiteNoise setelah `collectstatic`
- Media file tetap perlu dilayani oleh reverse proxy seperti Nginx
- SMTP harus valid jika endpoint aspiration submit dibuka ke publik
- Jika Anda memakai banyak gunicorn worker dan ingin analytics visitor lebih akurat, gunakan cache terpusat seperti Redis

## 11. Useful URLs

- Checker API: `/check-api/`
- API root: `/api/v1/`
- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`
- Raw schema: `/api/schema/`
