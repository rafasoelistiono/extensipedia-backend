# Extensipedia Backend

Backend Django untuk website dan dashboard admin Extensipedia.

Repo ini menyediakan:

- public API di `/api/v1/public/...`
- admin API di `/api/v1/admin/...`
- custom admin dashboard berbasis template di `/admin/`
- halaman checker sederhana di `/check-api/` untuk melihat hasil fetch API

## Apa Yang Perlu Diketahui

Kalau baru pertama kali buka repo ini, urutan paling cepatnya:

1. install dependency
2. isi `.env`
3. jalankan migration
4. jalankan server
5. buka `/admin/` untuk dashboard
6. buka `/api/schema/swagger-ui/` untuk melihat schema API
7. buka `/check-api/` untuk melihat checker halaman fetch API

`manage.py` di repo ini default memakai:

```txt
config.settings.dev
```

Jadi untuk local development normal, Anda cukup pakai:

```bash
python manage.py runserver
```

## Quick Start

### 1. Buat virtual environment

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Kalau PowerShell memblok activation:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 2. Isi `.env`

Buat file `.env` di root project kalau belum ada.

Contoh minimal:

```env
DJANGO_SECRET_KEY=change-me
DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DJANGO_DEFAULT_FROM_EMAIL=noreply@extensipedia.local
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
DJANGO_EMAIL_HOST=smtp.gmail.com
DJANGO_EMAIL_PORT=587
DJANGO_EMAIL_HOST_USER=your-email@gmail.com
DJANGO_EMAIL_HOST_PASSWORD=your-app-password
DJANGO_EMAIL_USE_TLS=True
DJANGO_EMAIL_USE_SSL=False
DJANGO_EMAIL_TIMEOUT=30
DATABASE_URL=postgresql://postgres:password@127.0.0.1:5432/extensipedia
JWT_ACCESS_TOKEN_MINUTES=15
JWT_REFRESH_TOKEN_DAYS=7
```

Catatan:

- project ini memakai PostgreSQL
- kalau fitur email ingin dites, isi SMTP dengan kredensial yang valid

### 3. Jalankan migration

```bash
python manage.py migrate
```

### 4. Jalankan server

```bash
python manage.py runserver
```

Kalau ingin eksplisit memakai interpreter venv:

```powershell
.\venv\Scripts\python.exe manage.py runserver
```

## URL Penting

Saat server aktif, URL yang paling sering dipakai:

- Home checker: `http://127.0.0.1:8000/check-api/`
- Custom admin dashboard: `http://127.0.0.1:8000/admin/`
- Django admin bawaan: `http://127.0.0.1:8000/django-admin/`
- API root: `http://127.0.0.1:8000/api/v1/`
- OpenAPI schema: `http://127.0.0.1:8000/api/schema/`
- Swagger UI: `http://127.0.0.1:8000/api/schema/swagger-ui/`
- ReDoc: `http://127.0.0.1:8000/api/schema/redoc/`

## Akun Dashboard Lokal

Saat `DEBUG=True`, akun dashboard lokal dibuat otomatis setelah migration.

Semua akun awal memakai password yang sama:

```txt
extensipedia.feb.ui
```

Daftar akun:

```txt
username: superadmin
akses: dashboard, tentang kami, akademik, kompetensi, karir, aspirasi, lacak tiket, profile

username: akademik
akses: dashboard, tentang kami, akademik, profile

username: kompetensi
akses: dashboard, tentang kami, kompetensi, profile

username: karir
akses: dashboard, tentang kami, karir, profile

username: advokasi
akses: dashboard, tentang kami, aspirasi, lacak tiket, profile
```

`Profile` dipakai untuk mengganti username dashboard dan password akun sendiri.


## Cara Memakai Repo Ini

### Untuk frontend developer

Paling berguna:

- buka [api.md](c:/projek/extensipedia-backend/api.md) untuk panduan endpoint yang lebih manusiawi
- buka Swagger UI untuk schema teknis
- buka `/check-api/` untuk melihat contoh hasil fetch public API secara visual

Yang biasa diambil frontend:

- About: hero, tentang kami, cabinet calendar
- Academic: quick downloads, repository, YouTube, countdown
- Competency: agenda cards
- Career: resources
- Advocacy: campaigns
- Aspirations: featured, submit, tracking

### Untuk admin/dashboard developer

Paling berguna:

- buka `/admin/`
- login dengan akun sesuai scope
- setiap akun hanya melihat menu yang memang boleh diakses
- gunakan menu `Profile` untuk mengganti kredensial akun lokal

### Untuk backend developer

Area utama project:

- `config/` = settings, URL utama, schema
- `about/` = konten tentang kami
- `academic/` = akademik
- `competency/` = kompetensi
- `career/` = karir
- `advocacy/` = campaign advokasi
- `aspirations/` = aspirasi publik dan moderasi admin
- `analytics_dashboard/` = data ringkasan dashboard
- `dashboard/` = custom admin dashboard template-based
- `core/` = utility umum, renderer, pagination, validators

## Alur Kerja Yang Paling Umum

### 1. Cek hasil public API

- buka `/check-api/`
- klik `Fetch` di section yang ingin dicek
- lihat preview dan raw JSON

### 2. Kelola konten admin

- buka `/admin/`
- login pakai akun dashboard
- edit section sesuai hak akses akun

### 3. Lihat dokumentasi API

- buka `/api/schema/swagger-ui/` untuk schema formal
- baca `api.md` untuk panduan implementasi frontend

### 4. Test aspiration submit

- bisa lewat halaman `/`
- atau POST ke `/api/v1/public/aspirations/submit/`
- kalau SMTP valid, backend akan mengirim email konfirmasi ke email yang diinput user

## Testing

Menjalankan seluruh test:

```bash
python manage.py test --settings=config.settings.test
```

Menjalankan test modul tertentu:

```bash
python manage.py test about.tests --settings=config.settings.test
python manage.py test dashboard.tests --settings=config.settings.test
```

## Seed Demo Data

Untuk mengisi data contoh:

```bash
python manage.py seed_demo_data
```

Data demo ini berguna untuk:

- konten public example
- featured aspirations
- career resources
- agenda kompetensi
- visitor analytics 30 hari untuk dashboard

## Troubleshooting Singkat

### Server jalan tapi login dashboard gagal

Cek:

- migration sudah dijalankan
- `DEBUG=True`
- akun lokal sudah dibuat

Lalu jalankan lagi:

```bash
python manage.py create_local_superadmin
```

### POST aspiration error karena URL tanpa slash

Gunakan endpoint standar:

```txt
/api/v1/public/aspirations/submit/
```

### Email tidak terkirim

Cek `.env`:

- `DJANGO_EMAIL_HOST`
- `DJANGO_EMAIL_HOST_USER`
- `DJANGO_EMAIL_HOST_PASSWORD`
- `DJANGO_EMAIL_USE_TLS`
- `DJANGO_EMAIL_USE_SSL`

Kalau pakai Gmail, gunakan App Password, bukan password Gmail biasa.

## Dokumen Yang Perlu Dibaca Setelah README

- [api.md](c:/projek/extensipedia-backend/api.md)
- [config/settings/base.py](c:/projek/extensipedia-backend/config/settings/base.py)
- [dashboard/services.py](c:/projek/extensipedia-backend/dashboard/services.py)
