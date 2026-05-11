# Extensipedia Fullstack Deployment Guide

Panduan ini memasang frontend Next.js dan backend Django pada satu VPS Ubuntu 22.04, dengan routing:

- `http://187.77.115.15/` -> Next.js frontend publik
- `http://187.77.115.15/admin/` -> backend admin dashboard
- `http://187.77.115.15/api/v1/` -> backend API
- `http://187.77.115.15/static/` -> backend static files
- `http://187.77.115.15/media/` -> backend uploaded media

Ganti `187.77.115.15` dengan IP/domain server yang dipakai. Jika sudah punya domain dan TLS, gunakan `https://domain.com` pada environment frontend dan backend.

## 1. Arsitektur Final

Service internal:

| Komponen | Internal address | Public path |
|---|---:|---|
| Next.js frontend | `127.0.0.1:3000` | `/`, `/_next/`, `/api/aspirations/` |
| Django backend | `127.0.0.1:8000` | `/admin/`, `/api/v1/`, `/django-admin/`, `/api/schema/`, `/check-api/` |
| Static backend | Nginx alias | `/static/` |
| Media backend | Nginx alias | `/media/` |

Prinsip penting:

- Jangan proxy `location /api/` ke backend.
- Hanya `/api/v1/` yang diarahkan ke backend.
- `/api/aspirations/` harus tetap ke Next karena itu API route internal frontend.
- Root `/` adalah milik frontend.
- Static dan media backend harus tetap tersedia untuk admin dan public media.

## 2. Persiapan Server

Masuk ke VPS lewat SSH.

```bash
ssh root@187.77.115.15
```

Update package.

```bash
sudo apt update
sudo apt upgrade -y
```

Install package dasar.

```bash
sudo apt install -y \
  git curl unzip nginx ufw \
  build-essential software-properties-common \
  postgresql postgresql-contrib libpq-dev \
  ca-certificates
```

Aktifkan firewall minimum.

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
sudo ufw status
```

## 3. Install Python untuk Django 6

Ubuntu 22.04 default memakai Python 3.10, sedangkan Django 6 butuh Python modern. Gunakan Python 3.13 atau 3.12.

```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3.13-dev
python3.13 --version
```

Jika PPA tidak tersedia di environment server, gunakan Python 3.12 dari PPA yang sama:

```bash
sudo apt install -y python3.12 python3.12-venv python3.12-dev
python3.12 --version
```

Di panduan ini contoh command memakai `python3.13`.

## 4. Install Node.js 20

Frontend memakai Next.js 16, React 19, dan Node minimal 20.9. Install Node 20 dari NodeSource.

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node -v
npm -v
```

Pastikan `node -v` minimal `v20.9.0`.

## 5. Buat Struktur Direktori

```bash
sudo useradd --system --create-home --home-dir /var/www/extensipedia --shell /bin/bash extensipedia || true
sudo usermod -aG www-data extensipedia
sudo mkdir -p /var/www/extensipedia
sudo chown -R extensipedia:www-data /var/www/extensipedia
sudo chmod 775 /var/www/extensipedia
cd /var/www/extensipedia
```

Clone backend dan frontend.

```bash
sudo -Hu extensipedia git clone https://github.com/rafasoelistiono/extensipedia-backend.git /var/www/extensipedia/backend
sudo -Hu extensipedia git clone https://github.com/rafasoelistiono/extensipedia-frontend.git /var/www/extensipedia/frontend
```

Jika repo private, login GitHub/token harus disiapkan dulu di server.

## 6. Setup Database PostgreSQL

Masuk ke PostgreSQL.

```bash
sudo -u postgres psql
```

Buat database dan user.

```sql
CREATE DATABASE extensipedia;
CREATE USER extensipedia_user WITH PASSWORD 'GANTI_PASSWORD_DATABASE_YANG_KUAT';
ALTER ROLE extensipedia_user SET client_encoding TO 'utf8';
ALTER ROLE extensipedia_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE extensipedia_user SET timezone TO 'Asia/Bangkok';
GRANT ALL PRIVILEGES ON DATABASE extensipedia TO extensipedia_user;
\c extensipedia
GRANT ALL ON SCHEMA public TO extensipedia_user;
\q
```

Test login database.

```bash
psql "postgresql://extensipedia_user:GANTI_PASSWORD_DATABASE_YANG_KUAT@127.0.0.1:5432/extensipedia" -c "select now();"
```

## 7. Setup Backend Django

Masuk ke folder backend.

```bash
sudo -Hu extensipedia bash -lc '
cd /var/www/extensipedia/backend
python3.13 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip wheel setuptools
python -m pip install -r requirements.txt
'
```

Buat secret key.

```bash
openssl rand -base64 48
```

Buat file `.env`.

```bash
nano /var/www/extensipedia/backend/.env
```

Isi untuk deployment IP-only HTTP:

```env
DJANGO_SECRET_KEY=GANTI_DENGAN_SECRET_KEY_PANJANG
DEBUG=False

DJANGO_ALLOWED_HOSTS=187.77.115.15,localhost,127.0.0.1
DJANGO_CORS_ALLOWED_ORIGINS=
DJANGO_CSRF_TRUSTED_ORIGINS=http://187.77.115.15

DATABASE_URL=postgresql://extensipedia_user:GANTI_PASSWORD_DATABASE_YANG_KUAT@127.0.0.1:5432/extensipedia

DJANGO_DEFAULT_FROM_EMAIL=your-email@gmail.com
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
DJANGO_EMAIL_HOST=smtp.gmail.com
DJANGO_EMAIL_PORT=465
DJANGO_EMAIL_HOST_USER=your-email@gmail.com
DJANGO_EMAIL_HOST_PASSWORD=your-gmail-app-password
DJANGO_EMAIL_USE_TLS=False
DJANGO_EMAIL_USE_SSL=True
DJANGO_EMAIL_TIMEOUT=30

JWT_ACCESS_TOKEN_MINUTES=15
JWT_REFRESH_TOKEN_DAYS=7

DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SESSION_COOKIE_SECURE=False
DJANGO_CSRF_COOKIE_SECURE=False
DJANGO_SECURE_HSTS_SECONDS=0
```

Jika sudah memakai domain HTTPS, ubah bagian host dan secure menjadi:

```env
DJANGO_ALLOWED_HOSTS=domain.com,www.domain.com,187.77.115.15,localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=https://domain.com,https://www.domain.com

DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SECURE_HSTS_SECONDS=31536000
```

Kunci permission `.env`.

```bash
sudo chown extensipedia:www-data /var/www/extensipedia/backend/.env
sudo chmod 600 /var/www/extensipedia/backend/.env
```

Jalankan migration dan collectstatic.

```bash
sudo -Hu extensipedia bash -lc '
cd /var/www/extensipedia/backend
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput
'
```

Jika ingin isi data contoh:

```bash
sudo -Hu extensipedia bash -lc '
cd /var/www/extensipedia/backend
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py seed_demo_data
'
```

Jika perlu akun dashboard lokal:

```bash
sudo -Hu extensipedia bash -lc '
cd /var/www/extensipedia/backend
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py create_local_superadmin
'
```

Catatan: command `create_local_superadmin` hanya untuk development lokal. Pada production dengan `DEBUG=False`, gunakan setup akun admin awal berikut.

### Setup akun hardcoded admin awal production

Gunakan script ini satu kali setelah `migrate`. Akun-akun ini dipakai untuk login pertama ke dashboard admin, lalu masing-masing pemilik akses wajib mengganti username/password dari menu `/admin/profile/`.

Akses awal yang dibuat:

| Akun | Scope | Akses dashboard |
|---|---|---|
| Superadmin | `full` | Semua menu dashboard |
| Akademik | `academic` | Dashboard, Tentang Kami, Akademik, Kompetensi, Profile |
| Kompetensi | `competency` | Dashboard, Tentang Kami, Kompetensi, Profile |
| Karir | `career` | Dashboard, Tentang Kami, Kompetensi, Karir, Profile |
| Advokasi | `advocacy` | Dashboard, Tentang Kami, Aspirasi, Lacak Tiket, Advokasi & Literasi Kebijakan, Profile |

Semua akun dibuat dengan `is_staff=True`. Hanya Superadmin yang dibuat dengan `is_superuser=True`; akun Akademik, Kompetensi, Karir, dan Advokasi tidak bisa mengakses menu khusus superadmin seperti manajemen user.

Ganti nilai `email`, `username`, `password`, dan `full_name` pada setiap akun sebelum menjalankan command.

Jika script lama 4 role sudah pernah dijalankan di VPS menggunakan heredoc seperti contoh di bawah, tidak ada file script yang perlu dihapus karena command tersebut hanya dieksekusi sekali di shell. Yang perlu dilakukan adalah menjalankan script baru 5 role di bawah agar akun lama diperbarui dan akun `karir` dibuat.

Jika sebelumnya Anda menyimpan script hardcoded ke file manual di VPS, hapus file manual tersebut setelah memastikan path-nya benar. Contoh:

```bash
sudo -Hu extensipedia bash <<'BASH'
cd /var/www/extensipedia/backend

# Jalankan hanya jika file ini memang pernah dibuat manual.
rm -f scripts/create_initial_admins.py
rm -f create_initial_admins.py
BASH
```

Opsional: jika ingin membersihkan akun lama yang memakai email placeholder sebelum menjalankan script baru, jalankan command ini. Lewati langkah ini jika akun lama sudah dipakai dan hanya ingin di-update.

```bash
sudo -Hu extensipedia bash <<'BASH'
cd /var/www/extensipedia/backend
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py shell <<'PY'
from django.contrib.auth import get_user_model

User = get_user_model()
placeholder_usernames = [
    "superadmin",
    "akademik",
    "kompetensi",
    "karir",
    "advokasi",
]

deleted, details = User.objects.filter(dashboard_username__in=placeholder_usernames).delete()
print(f"Akun placeholder terhapus: {deleted}")
print(details)
PY
BASH
```

Script baru 5 role:

```bash
sudo -Hu extensipedia bash <<'BASH'
cd /var/www/extensipedia/backend
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py shell <<'PY'
from django.contrib.auth import get_user_model

User = get_user_model()

accounts = [
    {
        "email": "owner@example.com",
        "username": "superadmin",
        "password": "GANTI_PASSWORD_SUPERADMIN_MINIMAL_8_CHAR",
        "full_name": "Owner Extensipedia",
        "scope": "full",
        "is_superuser": True,
    },
    {
        "email": "akademik@example.com",
        "username": "akademik",
        "password": "GANTI_PASSWORD_AKADEMIK_MINIMAL_8_CHAR",
        "full_name": "Admin Akademik",
        "scope": "academic",
        "is_superuser": False,
    },
    {
        "email": "kompetensi@example.com",
        "username": "kompetensi",
        "password": "GANTI_PASSWORD_KOMPETENSI_MINIMAL_8_CHAR",
        "full_name": "Admin Kompetensi",
        "scope": "competency",
        "is_superuser": False,
    },
    {
        "email": "karir@example.com",
        "username": "karir",
        "password": "GANTI_PASSWORD_KARIR_MINIMAL_8_CHAR",
        "full_name": "Admin Karir",
        "scope": "career",
        "is_superuser": False,
    },
    {
        "email": "advokasi@example.com",
        "username": "advokasi",
        "password": "GANTI_PASSWORD_ADVOKASI_MINIMAL_8_CHAR",
        "full_name": "Admin Advokasi",
        "scope": "advocacy",
        "is_superuser": False,
    },
]

for spec in accounts:
    username_conflict = (
        User.objects.exclude(email=spec["email"])
        .filter(dashboard_username__iexact=spec["username"])
        .first()
    )
    if username_conflict:
        raise SystemExit(
            f"dashboard_username '{spec['username']}' sudah dipakai oleh {username_conflict.email}."
        )

    user, created = User.objects.get_or_create(
        email=spec["email"],
        defaults={
            "dashboard_username": spec["username"],
            "full_name": spec["full_name"],
            "dashboard_access_scope": spec["scope"],
            "is_staff": True,
            "is_superuser": spec["is_superuser"],
            "is_active": True,
        },
    )

    user.dashboard_username = spec["username"]
    user.full_name = spec["full_name"]
    user.dashboard_access_scope = spec["scope"]
    user.is_staff = True
    user.is_superuser = spec["is_superuser"]
    user.is_active = True
    user.set_password(spec["password"])
    user.save(
        update_fields=[
            "dashboard_username",
            "full_name",
            "dashboard_access_scope",
            "is_staff",
            "is_superuser",
            "is_active",
            "password",
            "updated_at",
        ]
    )

    print(
        "Admin awal siap: "
        f"username={user.dashboard_username}; email={user.email}; "
        f"scope={user.dashboard_access_scope}; superuser={user.is_superuser}; created={created}"
    )
PY
BASH
```

Login dashboard HTML:

- URL: `http://187.77.115.15/admin/` atau `https://domain.com/admin/`
- Username: nilai `username` masing-masing akun, contoh `superadmin`, `akademik`, `kompetensi`, `karir`, atau `advokasi`
- Password: nilai `password` masing-masing akun

Login Admin API:

```bash
curl -X POST http://187.77.115.15/api/v1/admin/accounts/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"akademik@example.com","password":"GANTI_PASSWORD_AKADEMIK_MINIMAL_8_CHAR"}'
```

Dashboard HTML memakai `username` untuk login, sedangkan Admin API memakai `email`. Setelah login pertama, setiap pemilik akses harus membuka `/admin/profile/` lalu mengganti username dashboard dan password. Jangan jalankan ulang script ini setelah pemilik akses mengganti password karena script akan mengatur ulang username/password ke nilai hardcoded.

Test backend manual.

```bash
sudo -Hu extensipedia bash -lc '
cd /var/www/extensipedia/backend
export DJANGO_SETTINGS_MODULE=config.settings.prod
venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2 --timeout 120
'
```

Buka terminal lain dan test:

```bash
curl http://127.0.0.1:8000/api/v1/
```

Stop gunicorn manual dengan `CTRL+C`.

## 8. Setup Frontend Next.js

Masuk folder frontend.

```bash
cd /var/www/extensipedia/frontend
sudo -Hu extensipedia npm ci
```

Buat env production.

```bash
nano /var/www/extensipedia/frontend/.env.production
```

Isi untuk IP-only HTTP:

```env
NEXT_PUBLIC_SITE_URL=http://187.77.115.15
NEXT_PUBLIC_API_BASE_URL=http://187.77.115.15
```

Jika memakai domain HTTPS:

```env
NEXT_PUBLIC_SITE_URL=https://domain.com
NEXT_PUBLIC_API_BASE_URL=https://domain.com
```

Aturan penting:

- Isi `NEXT_PUBLIC_API_BASE_URL` dengan origin saja.
- Jangan tambahkan `/api/v1`.
- Jangan isi production dengan `http://127.0.0.1:8000`.

Kunci permission env frontend.

```bash
sudo chown extensipedia:www-data /var/www/extensipedia/frontend/.env.production
sudo chmod 640 /var/www/extensipedia/frontend/.env.production
```

Build frontend.

```bash
cd /var/www/extensipedia/frontend
sudo -Hu extensipedia npm run build
```

Test manual.

```bash
cd /var/www/extensipedia/frontend
sudo -Hu extensipedia npm run start -- -H 127.0.0.1 -p 3000
```

Buka terminal lain dan test:

```bash
curl -I http://127.0.0.1:3000/
curl -I http://127.0.0.1:3000/_next/
```

Stop manual dengan `CTRL+C`.

## 9. Buat Service systemd Backend

Buat service file.

```bash
sudo nano /etc/systemd/system/extensipedia-backend.service
```

Isi:

```ini
[Unit]
Description=Extensipedia Django Backend
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=extensipedia
Group=www-data
WorkingDirectory=/var/www/extensipedia/backend
Environment=DJANGO_SETTINGS_MODULE=config.settings.prod
ExecStart=/var/www/extensipedia/backend/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2 --timeout 120 --access-logfile - --error-logfile -
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Pastikan user aplikasi bisa membaca backend dan menulis media.

```bash
sudo chown -R extensipedia:www-data /var/www/extensipedia/backend
sudo chmod -R 755 /var/www/extensipedia/backend
sudo chmod -R 775 /var/www/extensipedia/backend/media
sudo chmod 600 /var/www/extensipedia/backend/.env
sudo chown extensipedia:www-data /var/www/extensipedia/backend/.env
```

Aktifkan service.

```bash
sudo systemctl daemon-reload
sudo systemctl enable extensipedia-backend
sudo systemctl start extensipedia-backend
sudo systemctl status extensipedia-backend --no-pager
```

Lihat log backend:

```bash
sudo journalctl -u extensipedia-backend -f
```

## 10. Buat Service systemd Frontend

Buat service file.

```bash
sudo nano /etc/systemd/system/extensipedia-frontend.service
```

Isi:

```ini
[Unit]
Description=Extensipedia Next.js Frontend
After=network.target

[Service]
Type=simple
User=extensipedia
Group=www-data
WorkingDirectory=/var/www/extensipedia/frontend
Environment=NODE_ENV=production
ExecStart=/usr/bin/npm run start -- -H 127.0.0.1 -p 3000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Pastikan user aplikasi bisa membaca frontend.

```bash
sudo chown -R extensipedia:www-data /var/www/extensipedia/frontend
sudo chmod -R 755 /var/www/extensipedia/frontend
```

Aktifkan service.

```bash
sudo systemctl daemon-reload
sudo systemctl enable extensipedia-frontend
sudo systemctl start extensipedia-frontend
sudo systemctl status extensipedia-frontend --no-pager
```

Lihat log frontend:

```bash
sudo journalctl -u extensipedia-frontend -f
```

## 11. Konfigurasi Nginx

Buat config.

```bash
sudo nano /etc/nginx/sites-available/extensipedia
```

Isi untuk IP-only HTTP:

```nginx
server {
    listen 80;
    server_name 187.77.115.15 _;

    client_max_body_size 20m;

    location ^~ /static/ {
        alias /var/www/extensipedia/backend/staticfiles/;
        access_log off;
        expires 30d;
        add_header Cache-Control "public";
    }

    location ^~ /media/ {
        alias /var/www/extensipedia/backend/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    location ^~ /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /django-admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /api/v1/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /api/schema/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /check-api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /api/aspirations/ {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ^~ /_next/ {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Aktifkan config.

```bash
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/extensipedia /etc/nginx/sites-enabled/extensipedia
sudo nginx -t
sudo systemctl reload nginx
```

## 12. HTTPS Jika Sudah Punya Domain

Public certificate seperti Let's Encrypt normalnya butuh domain. Untuk IP-only, gunakan HTTP dulu.

Jika domain sudah diarahkan ke IP VPS:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d domain.com -d www.domain.com
```

Setelah HTTPS aktif:

1. Ubah backend `.env`:

```env
DJANGO_ALLOWED_HOSTS=domain.com,www.domain.com,187.77.115.15,localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=https://domain.com,https://www.domain.com
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SECURE_HSTS_SECONDS=31536000
```

2. Ubah frontend `.env.production`:

```env
NEXT_PUBLIC_SITE_URL=https://domain.com
NEXT_PUBLIC_API_BASE_URL=https://domain.com
```

3. Rebuild frontend dan restart service:

```bash
cd /var/www/extensipedia/frontend
sudo -Hu extensipedia npm run build
sudo systemctl restart extensipedia-frontend
sudo systemctl restart extensipedia-backend
sudo nginx -t
sudo systemctl reload nginx
```

## 13. Verifikasi Setelah Deploy

Cek service internal:

```bash
curl http://127.0.0.1:8000/api/v1/
curl -I http://127.0.0.1:3000/
```

Cek public route dari server:

```bash
curl -I http://187.77.115.15/
curl -I http://187.77.115.15/akademik
curl -I http://187.77.115.15/kompetensi-karir
curl -I http://187.77.115.15/karir
curl -I http://187.77.115.15/advokasi
curl -I http://187.77.115.15/tentang-kami
curl -I http://187.77.115.15/sitemap.xml
curl -I http://187.77.115.15/admin/
curl http://187.77.115.15/api/v1/
curl http://187.77.115.15/api/v1/public/aspirations/featured/
```

Cek bahwa Next API route tetap ke frontend:

```bash
curl -I "http://187.77.115.15/api/aspirations/track?ticket_id=ASP-XXXXXXXXXX"
```

Cek static admin:

```bash
curl -I http://187.77.115.15/static/
```

Cek media jika ada file:

```bash
curl -I http://187.77.115.15/media/path/to/file.jpg
```

## 14. Test Submit Aspirasi Production

Karena aturan submit aspirasi saat ini adalah email harus sukses dulu sebelum ticket dikembalikan, pastikan SMTP production valid.

Test dari server:

```bash
cd /var/www/extensipedia/backend
sudo -Hu extensipedia venv/bin/python manage.py shell --settings=config.settings.prod
```

Di shell:

```python
from django.conf import settings
from aspirations.models import AspirationSubmission
from aspirations.services import send_aspiration_confirmation_email

aspiration = AspirationSubmission(
    ticket_id="ASP-SMTPTEST1",
    full_name="SMTP Test",
    npm="00000000",
    email=settings.EMAIL_HOST_USER,
    title="Test SMTP production",
    short_description="Test pengiriman email production.",
)
send_aspiration_confirmation_email(aspiration)
```

Jika tidak error, SMTP berhasil.

Test endpoint submit:

```bash
curl -X POST http://187.77.115.15/api/v1/public/aspirations/submit/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Production Test",
    "npm": "00000000",
    "email": "your-email@gmail.com",
    "title": "Test submit production",
    "short_description": "Validasi submit aspirasi production."
  }'
```

Expected sukses:

```json
{
  "success": true,
  "message": "Aspiration submitted successfully",
  "data": {
    "ticket_id": "ASP-XXXXXXXXXX"
  }
}
```

Jika SMTP gagal, expected:

```json
{
  "success": false,
  "message": "Aspiration ticket could not be submitted because the confirmation email could not be sent.",
  "data": {
    "detail": "Aspiration ticket could not be submitted because the confirmation email could not be sent."
  }
}
```

Pada kasus gagal, ticket tidak dibuat.

## 15. Cara Update Backend

Backup database dulu.

```bash
mkdir -p /var/www/extensipedia/backups
pg_dump "postgresql://extensipedia_user:GANTI_PASSWORD_DATABASE_YANG_KUAT@127.0.0.1:5432/extensipedia" \
  > /var/www/extensipedia/backups/extensipedia_$(date +%Y%m%d_%H%M%S).sql
```

Update kode backend.

```bash
cd /var/www/extensipedia/backend
sudo -Hu extensipedia git pull origin main
sudo -Hu extensipedia venv/bin/python -m pip install -r requirements.txt
sudo -Hu extensipedia env DJANGO_SETTINGS_MODULE=config.settings.prod venv/bin/python manage.py migrate
sudo -Hu extensipedia env DJANGO_SETTINGS_MODULE=config.settings.prod venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart extensipedia-backend
sudo systemctl status extensipedia-backend --no-pager
```

Cek log jika ada error.

```bash
sudo journalctl -u extensipedia-backend -n 100 --no-pager
```

## 16. Cara Update Frontend

Update kode frontend.

```bash
cd /var/www/extensipedia/frontend
sudo -Hu extensipedia git pull origin main
sudo -Hu extensipedia npm ci
sudo -Hu extensipedia npm run build
sudo systemctl restart extensipedia-frontend
sudo systemctl status extensipedia-frontend --no-pager
```

Cek log jika ada error.

```bash
sudo journalctl -u extensipedia-frontend -n 100 --no-pager
```

## 17. Cara Update Nginx

Setelah mengubah config Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Jika gagal, jangan reload sebelum `nginx -t` sukses.

## 18. Troubleshooting

### Root `/` tidak membuka frontend

Cek service frontend:

```bash
sudo systemctl status extensipedia-frontend --no-pager
sudo journalctl -u extensipedia-frontend -n 100 --no-pager
curl -I http://127.0.0.1:3000/
```

### `/api/v1/` tidak membuka backend

Cek service backend:

```bash
sudo systemctl status extensipedia-backend --no-pager
sudo journalctl -u extensipedia-backend -n 100 --no-pager
curl http://127.0.0.1:8000/api/v1/
```

### Admin tampil tanpa CSS

Kemungkinan `/static/` salah route atau `collectstatic` belum dijalankan.

```bash
cd /var/www/extensipedia/backend
sudo -Hu extensipedia env DJANGO_SETTINGS_MODULE=config.settings.prod venv/bin/python manage.py collectstatic --noinput
sudo nginx -t
sudo systemctl reload nginx
```

Pastikan Nginx punya:

```nginx
location ^~ /static/ {
    alias /var/www/extensipedia/backend/staticfiles/;
}
```

### Media tidak tampil

Pastikan file memang ada di:

```bash
ls -lah /var/www/extensipedia/backend/media
```

Pastikan Nginx punya:

```nginx
location ^~ /media/ {
    alias /var/www/extensipedia/backend/media/;
}
```

### `/api/aspirations/submit` gagal

Cek Nginx tidak punya `location /api/` generik ke backend.

Yang benar:

```nginx
location ^~ /api/v1/ {
    proxy_pass http://127.0.0.1:8000;
}

location ^~ /api/aspirations/ {
    proxy_pass http://127.0.0.1:3000;
}
```

### Submit aspirasi return `503`

Artinya SMTP gagal, dan ticket memang tidak dibuat. Cek log:

```bash
sudo journalctl -u extensipedia-backend -n 100 --no-pager
```

Cek `.env` backend:

```env
DJANGO_EMAIL_HOST=smtp.gmail.com
DJANGO_EMAIL_PORT=465
DJANGO_EMAIL_USE_TLS=False
DJANGO_EMAIL_USE_SSL=True
DJANGO_EMAIL_HOST_USER=your-email@gmail.com
DJANGO_EMAIL_HOST_PASSWORD=your-gmail-app-password
DJANGO_DEFAULT_FROM_EMAIL=your-email@gmail.com
```

Untuk Gmail, gunakan App Password, bukan password login Gmail biasa.

### Production memakai HTTPS tapi redirect atau CSRF bermasalah

Pastikan Nginx mengirim header:

```nginx
proxy_set_header X-Forwarded-Proto $scheme;
```

Pastikan backend `.env`:

```env
DJANGO_CSRF_TRUSTED_ORIGINS=https://domain.com
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
```

### Production masih memakai localhost di sitemap/media

Rebuild frontend setelah `.env.production` diubah:

```bash
cd /var/www/extensipedia/frontend
sudo -Hu extensipedia npm run build
sudo systemctl restart extensipedia-frontend
```

## 19. Checklist Final

- [ ] `http://187.77.115.15/` membuka frontend.
- [ ] `http://187.77.115.15/akademik` membuka halaman akademik.
- [ ] `http://187.77.115.15/kompetensi-karir` membuka halaman kompetensi karir.
- [ ] `http://187.77.115.15/karir` membuka halaman karir.
- [ ] `http://187.77.115.15/advokasi` membuka halaman advokasi.
- [ ] `http://187.77.115.15/tentang-kami` membuka halaman tentang kami.
- [ ] `http://187.77.115.15/sitemap.xml` tidak memakai localhost.
- [ ] `http://187.77.115.15/admin/` membuka backend admin dengan CSS.
- [ ] `http://187.77.115.15/api/v1/` dijawab backend.
- [ ] `http://187.77.115.15/api/v1/public/aspirations/featured/` dijawab backend.
- [ ] `http://187.77.115.15/api/aspirations/track?ticket_id=...` dijawab Next API route.
- [ ] `/static/` diarahkan ke backend staticfiles.
- [ ] `/media/` diarahkan ke backend media.
- [ ] Submit aspirasi mengirim email dan baru mengembalikan `ticket_id` setelah email sukses.

## 20. Migrasi dari IP VPS ke Domain `extensipedia.com` lewat Domainesia

Bagian ini untuk kondisi aplikasi sudah berjalan dari IP VPS, lalu domain `extensipedia.com` yang dibeli di Domainesia ingin diarahkan ke VPS yang sama.

Target akhir:

- `https://extensipedia.com/` -> frontend Next.js
- `https://extensipedia.com/admin/` -> backend admin dashboard
- `https://extensipedia.com/api/v1/` -> backend API
- `https://extensipedia.com/static/` -> backend static files
- `https://extensipedia.com/media/` -> backend uploaded media

Contoh ini memakai IP VPS aktual `187.77.115.15`. Jika IP VPS berubah, pakai IP yang saat ini berhasil membuka website lewat browser.

### 20.1 Requirement sebelum mulai

Pastikan syarat ini sudah terpenuhi:

- Website sudah bisa dibuka lewat `http://187.77.115.15/`.
- Service backend dan frontend sudah aktif.
- Nginx sudah menjadi reverse proxy untuk frontend dan backend.
- Domain `extensipedia.com` sudah aktif di akun Domainesia.
- Nameserver domain memakai nameserver Domainesia jika DNS diedit dari menu Domainesia.
- Port `80` dan `443` terbuka di firewall VPS.
- Kamu punya akses login ke panel Domainesia dan akses SSH ke VPS.

Cek service di VPS:

```bash
sudo systemctl status nginx --no-pager
sudo systemctl status extensipedia-frontend --no-pager
sudo systemctl status extensipedia-backend --no-pager
sudo ufw status
```

Jika Nginx belum diizinkan di firewall:

```bash
sudo ufw allow 'Nginx Full'
sudo ufw status
```

### 20.2 Cek nameserver di Domainesia

Masuk ke panel Domainesia:

1. Login ke Domainesia.
2. Buka `My Domains`.
3. Klik domain `extensipedia.com`.
4. Buka menu `Nameservers`.

Jika nameserver masih default Domainesia, lanjut edit DNS dari menu `DNS Management`.

Jika nameserver sudah diarahkan ke Cloudflare atau provider lain, record DNS harus diedit di provider tersebut, bukan di halaman `DNS Management` Domainesia. Menu `DNS Management` Domainesia hanya efektif jika nameserver domain memang memakai Domainesia.

### 20.3 Update DNS Management Domainesia

Dari screenshot Domainesia, saat ini ada dua record:

| Host Name | Record Type | Address sekarang |
|---|---|---:|
| `extensipedia.com` | `A (Address)` | `76.76.21.21` |
| `www` | `A (Address)` | `76.76.21.21` |

`76.76.21.21` bukan IP VPS aplikasi. Ganti `Address` kedua record itu menjadi IP VPS `187.77.115.15`.

Di panel Domainesia:

1. Buka `My Domains`.
2. Klik `extensipedia.com`.
3. Buka menu `DNS Management`.
4. Pada baris `Host Name` = `extensipedia.com`, pilih `Record Type` = `A (Address)`, isi `Address` = `187.77.115.15`.
5. Pada baris `Host Name` = `www`, pilih `Record Type` = `A (Address)`, isi `Address` = `187.77.115.15`.
6. Biarkan `Priority` kosong atau `N/A` karena priority hanya untuk record `MX`.
7. Klik `Save Changes`.

Hasil record yang benar:

| Host Name | Record Type | Address | Priority |
|---|---|---:|---|
| `extensipedia.com` | `A (Address)` | `187.77.115.15` | `N/A` |
| `www` | `A (Address)` | `187.77.115.15` | `N/A` |

Catatan penting:

- Jangan isi `http://` atau `https://` di kolom `Address`.
- Jangan isi path seperti `/admin` atau `/api/v1` di DNS.
- DNS hanya mengarahkan domain ke IP server. Routing `/`, `/admin/`, dan `/api/v1/` tetap diatur oleh Nginx.
- Jika ada record `AAAA` IPv6 yang mengarah ke server lain, hapus dulu kecuali VPS memang punya IPv6 yang benar.
- Jika ada record `CAA`, pastikan Let's Encrypt diizinkan, atau hapus sementara sebelum membuat HTTPS.

Tunggu DNS propagate. Biasanya beberapa menit, tetapi bisa sampai 24 jam.

Cek dari laptop atau server:

```bash
nslookup extensipedia.com 1.1.1.1
nslookup www.extensipedia.com 1.1.1.1
```

Jika memakai `dig`:

```bash
dig +short extensipedia.com
dig +short www.extensipedia.com
```

Expected:

```text
187.77.115.15
```

Jika di VPS belum ada `dig`:

```bash
sudo apt install -y dnsutils
```

Jangan lanjut ke Certbot sebelum `extensipedia.com` dan `www.extensipedia.com` resolve ke IP VPS yang benar.

### 20.4 Update Nginx agar menerima domain

Edit config Nginx:

```bash
sudo nano /etc/nginx/sites-available/extensipedia
```

Ubah `server_name` pada server port `80` dari IP-only:

```nginx
server_name 187.77.115.15 _;
```

menjadi:

```nginx
server_name extensipedia.com www.extensipedia.com 187.77.115.15;
```

Pastikan routing penting tetap seperti ini:

```nginx
location ^~ /static/ {
    alias /var/www/extensipedia/backend/staticfiles/;
}

location ^~ /media/ {
    alias /var/www/extensipedia/backend/media/;
}

location ^~ /admin/ {
    proxy_pass http://127.0.0.1:8000;
}

location ^~ /api/v1/ {
    proxy_pass http://127.0.0.1:8000;
}

location ^~ /api/aspirations/ {
    proxy_pass http://127.0.0.1:3000;
}

location / {
    proxy_pass http://127.0.0.1:3000;
}
```

Pastikan setiap blok `proxy_pass` tetap punya header ini:

```nginx
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

Test dan reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Cek HTTP domain sebelum HTTPS:

```bash
curl -I http://extensipedia.com/
curl -I http://www.extensipedia.com/
```

Jika masih mengarah ke `76.76.21.21`, DNS belum berubah atau belum propagate.

### 20.5 Pasang HTTPS Let's Encrypt

Jalankan Certbot hanya setelah DNS sudah mengarah ke IP VPS.

Install Certbot:

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

Buat certificate untuk root domain dan `www`:

```bash
sudo certbot --nginx -d extensipedia.com -d www.extensipedia.com
```

Saat Certbot bertanya redirect HTTP ke HTTPS, pilih opsi redirect jika tersedia.

Test auto-renew certificate:

```bash
sudo certbot renew --dry-run
```

Cek hasil Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 20.6 Update environment backend Django

Edit `.env` backend:

```bash
sudo nano /var/www/extensipedia/backend/.env
```

Ubah bagian host dan HTTPS menjadi:

```env
DJANGO_ALLOWED_HOSTS=extensipedia.com,www.extensipedia.com,187.77.115.15,localhost,127.0.0.1
DJANGO_CORS_ALLOWED_ORIGINS=
DJANGO_CSRF_TRUSTED_ORIGINS=https://extensipedia.com,https://www.extensipedia.com

DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SECURE_HSTS_SECONDS=31536000
```

Catatan:

- `DJANGO_ALLOWED_HOSTS` wajib memuat domain dan IP VPS.
- `DJANGO_CSRF_TRUSTED_ORIGINS` wajib memakai `https://`, bukan hanya nama domain.
- `DJANGO_CORS_ALLOWED_ORIGINS` boleh kosong karena frontend dan backend ada di origin yang sama.
- Aktifkan value HTTPS setelah certificate berhasil.

Pastikan permission `.env` tetap aman:

```bash
sudo chown extensipedia:www-data /var/www/extensipedia/backend/.env
sudo chmod 600 /var/www/extensipedia/backend/.env
```

Restart backend:

```bash
sudo systemctl restart extensipedia-backend
sudo systemctl status extensipedia-backend --no-pager
```

### 20.7 Update environment frontend Next.js

Edit `.env.production` frontend:

```bash
sudo nano /var/www/extensipedia/frontend/.env.production
```

Isi:

```env
NEXT_PUBLIC_SITE_URL=https://extensipedia.com
NEXT_PUBLIC_API_BASE_URL=https://extensipedia.com
```

Aturan penting:

- `NEXT_PUBLIC_API_BASE_URL` diisi origin saja.
- Jangan tambahkan `/api/v1`.
- Jangan pakai `http://127.0.0.1:8000` di production.
- Karena env `NEXT_PUBLIC_*` dibaca saat build, frontend wajib di-build ulang setelah env berubah.

Build ulang dan restart frontend:

```bash
cd /var/www/extensipedia/frontend
sudo -Hu extensipedia npm ci
sudo -Hu extensipedia npm run build
sudo systemctl restart extensipedia-frontend
sudo systemctl status extensipedia-frontend --no-pager
```

### 20.8 Deploy/reload setelah domain aktif

Urutan deploy normal setelah domain aktif:

```bash
# Backend
cd /var/www/extensipedia/backend
sudo -Hu extensipedia git pull origin main
sudo -Hu extensipedia venv/bin/python -m pip install -r requirements.txt
sudo -Hu extensipedia env DJANGO_SETTINGS_MODULE=config.settings.prod venv/bin/python manage.py migrate
sudo -Hu extensipedia env DJANGO_SETTINGS_MODULE=config.settings.prod venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart extensipedia-backend

# Frontend
cd /var/www/extensipedia/frontend
sudo -Hu extensipedia git pull origin main
sudo -Hu extensipedia npm ci
sudo -Hu extensipedia npm run build
sudo systemctl restart extensipedia-frontend

# Nginx
sudo nginx -t
sudo systemctl reload nginx
```

Jika hanya mengubah DNS di Domainesia, tidak perlu restart service. Tunggu DNS propagate, lalu verifikasi.

Jika hanya mengubah Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Jika hanya mengubah backend `.env`:

```bash
sudo systemctl restart extensipedia-backend
```

Jika hanya mengubah frontend `.env.production`, wajib build ulang:

```bash
cd /var/www/extensipedia/frontend
sudo -Hu extensipedia npm run build
sudo systemctl restart extensipedia-frontend
```

### 20.9 Verifikasi domain dan HTTPS

Cek DNS:

```bash
dig +short extensipedia.com
dig +short www.extensipedia.com
```

Expected:

```text
187.77.115.15
```

Cek dari server:

```bash
curl -I https://extensipedia.com/
curl -I https://extensipedia.com/akademik
curl -I https://extensipedia.com/kompetensi-karir
curl -I https://extensipedia.com/karir
curl -I https://extensipedia.com/advokasi
curl -I https://extensipedia.com/tentang-kami
curl -I https://extensipedia.com/sitemap.xml
curl -I https://extensipedia.com/admin/
curl https://extensipedia.com/api/v1/
curl https://extensipedia.com/api/v1/public/aspirations/featured/
curl -I "https://extensipedia.com/api/aspirations/track?ticket_id=ASP-XXXXXXXXXX"
```

Cek redirect HTTP ke HTTPS:

```bash
curl -I http://extensipedia.com/
curl -I http://www.extensipedia.com/
```

Expected ada status `301` atau `308` menuju `https://...`.

Cek certificate:

```bash
sudo certbot certificates
```

### 20.10 Troubleshooting Domainesia

Jika domain masih membuka halaman lama atau tidak membuka VPS:

```bash
dig +short extensipedia.com
dig +short www.extensipedia.com
```

Jika output masih `76.76.21.21`, berarti DNS Domainesia belum terganti, belum tersimpan, atau nameserver domain tidak memakai Domainesia.

Cek di Domainesia:

- Menu `DNS Management`: record `extensipedia.com` dan `www` harus `A (Address)` ke `187.77.115.15`.
- Menu `Nameservers`: pastikan nameserver aktif adalah milik Domainesia jika DNS dikelola dari Domainesia.
- Tidak ada record `AAAA` yang mengarah ke server lain.
- Tidak memakai `Blogger Settings`, parking, atau domain forwarding untuk website ini.

Jika Certbot gagal:

```bash
dig +short extensipedia.com
dig +short www.extensipedia.com
sudo nginx -t
sudo journalctl -u nginx -n 100 --no-pager
```

Penyebab umum:

- DNS belum mengarah ke `187.77.115.15`.
- Port `80` ditutup firewall VPS atau security group provider.
- `server_name` Nginx belum memuat `extensipedia.com`.
- Nameserver domain bukan Domainesia, tetapi DNS diedit di Domainesia.
- Ada record `AAAA` mengarah ke IPv6 yang salah.
- Ada proxy/CDN yang menghalangi HTTP challenge.

Jika admin/API kena CSRF atau redirect loop:

```bash
sudo journalctl -u extensipedia-backend -n 100 --no-pager
```

Pastikan Nginx tetap mengirim:

```nginx
proxy_set_header X-Forwarded-Proto $scheme;
```

Pastikan backend `.env` memakai:

```env
DJANGO_CSRF_TRUSTED_ORIGINS=https://extensipedia.com,https://www.extensipedia.com
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
```

Jika sitemap, fetch API, atau media masih memakai IP/localhost:

```bash
cat /var/www/extensipedia/frontend/.env.production
cd /var/www/extensipedia/frontend
sudo -Hu extensipedia npm run build
sudo systemctl restart extensipedia-frontend
```

### 20.11 Log konteks migrasi Domainesia ke HTTPS

Log ini adalah catatan kejadian saat migrasi `extensipedia.com` dari akses IP VPS ke domain HTTPS pada Rabu, 6 Mei 2026.

DNS Domainesia sudah mengarah ke IP VPS aktual:

```bash
nslookup extensipedia.com 1.1.1.1
nslookup www.extensipedia.com 1.1.1.1
curl -4 ifconfig.me
```

Output penting:

```text
Name:   extensipedia.com
Address: 187.77.115.15

Name:   www.extensipedia.com
Address: 187.77.115.15

187.77.115.15
```

HTTP sebelum HTTPS sudah masuk ke Nginx dan Next.js:

```bash
curl -I http://extensipedia.com/
curl -I http://www.extensipedia.com/
```

Output penting:

```text
HTTP/1.1 200 OK
Server: nginx/1.18.0 (Ubuntu)
X-Powered-By: Next.js
```

Saat pertama menjalankan Certbot, certificate berhasil dibuat tetapi gagal dipasang otomatis ke Nginx:

```bash
sudo certbot --nginx -d extensipedia.com -d www.extensipedia.com
```

Output penting:

```text
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/extensipedia.com/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/extensipedia.com/privkey.pem
This certificate expires on 2026-08-04.

Could not automatically find a matching server block for extensipedia.com.
Set the `server_name` directive to use the Nginx installer.
```

Penyebabnya adalah Nginx masih memakai `server_name` IP-only:

```bash
sudo grep -R "server_name" -n /etc/nginx/sites-available /etc/nginx/sites-enabled
```

Output penting:

```text
/etc/nginx/sites-available/extensipedia:3:    server_name 187.77.115.15 _;
/etc/nginx/sites-enabled/extensipedia:3:    server_name 187.77.115.15 _;
```

Fix yang dilakukan:

```nginx
server_name extensipedia.com www.extensipedia.com 187.77.115.15;
```

Setelah Nginx valid dan reload, certificate yang sudah dibuat berhasil dipasang:

```bash
sudo nginx -t
sudo systemctl reload nginx
sudo certbot install --cert-name extensipedia.com
```

Output penting:

```text
nginx: configuration file /etc/nginx/nginx.conf test is successful
Successfully deployed certificate for extensipedia.com to /etc/nginx/sites-enabled/extensipedia
Successfully deployed certificate for www.extensipedia.com to /etc/nginx/sites-enabled/extensipedia
```

Verifikasi HTTPS berhasil:

```bash
curl -I https://extensipedia.com/
curl -I https://www.extensipedia.com/
curl -I http://extensipedia.com/
```

Output penting:

```text
https://extensipedia.com/      -> HTTP/1.1 200 OK
https://www.extensipedia.com/  -> HTTP/1.1 200 OK
http://extensipedia.com/       -> HTTP/1.1 301 Moved Permanently
Location: https://extensipedia.com/
```

Backend dan frontend env kemudian diubah ke domain HTTPS, backend di-restart, frontend di-build ulang, lalu Nginx di-reload:

```bash
sudo systemctl restart extensipedia-backend

cd /var/www/extensipedia/frontend
sudo -Hu extensipedia npm run build
sudo systemctl restart extensipedia-frontend

sudo nginx -t
sudo systemctl reload nginx
```

Build frontend berhasil:

```text
Next.js 16.1.6 (Turbopack)
Environments: .env.production
Compiled successfully
Finished TypeScript
Generating static pages (12/12)
```

Route production berhasil setelah HTTPS:

```bash
curl -I https://extensipedia.com/admin/
curl https://extensipedia.com/api/v1/
curl https://extensipedia.com/api/v1/public/aspirations/featured/
curl -I "https://extensipedia.com/api/aspirations/track?ticket_id=ASP-AAAABBBBCC"
```

Output penting:

```text
/admin/ -> HTTP/1.1 302 Found
Location: /admin/login/

/api/v1/ -> {"success":true,"message":"Extensipedia API v1",...}

/api/v1/public/aspirations/featured/ -> {"success":true,"message":"Featured aspirations retrieved successfully",...}

/api/aspirations/track?ticket_id=ASP-AAAABBBBCC -> HTTP/1.1 200 OK
```

Auto-renew certificate berhasil disimulasikan:

```bash
sudo certbot renew --dry-run
sudo certbot certificates
```

Output penting:

```text
Congratulations, all simulated renewals succeeded:
  /etc/letsencrypt/live/extensipedia.com/fullchain.pem (success)

Certificate Name: extensipedia.com
Domains: extensipedia.com www.extensipedia.com
Expiry Date: 2026-08-04 07:38:49+00:00 (VALID: 89 days)
Certificate Path: /etc/letsencrypt/live/extensipedia.com/fullchain.pem
Private Key Path: /etc/letsencrypt/live/extensipedia.com/privkey.pem
```

### 20.12 Migrasi domain dari `extensipedia.com` ke `bempefebui.com`

Bagian ini untuk kondisi `extensipedia.com` sudah berhasil berjalan di Domainesia dan HTTPS, lalu domain utama ingin diganti menjadi `bempefebui.com` pada VPS dan platform Domainesia yang sama.

Target akhir:

- `https://bempefebui.com/` -> frontend Next.js
- `https://bempefebui.com/admin/` -> backend admin dashboard
- `https://bempefebui.com/api/v1/` -> backend API
- `https://bempefebui.com/static/` -> backend static files
- `https://bempefebui.com/media/` -> backend uploaded media
- `http://bempefebui.com/` dan `http://www.bempefebui.com/` redirect ke HTTPS

Contoh ini tetap memakai IP VPS aktual `187.77.115.15`. Jika IP VPS berubah, pakai IP VPS yang benar saat migrasi.

#### 20.12.1 Cek service dan backup config

Masuk ke VPS:

```bash
ssh root@187.77.115.15
```

Cek service:

```bash
sudo systemctl status nginx --no-pager
sudo systemctl status extensipedia-backend --no-pager
sudo systemctl status extensipedia-frontend --no-pager
sudo ufw status
```

Backup config sebelum edit:

```bash
sudo cp /etc/nginx/sites-available/extensipedia /etc/nginx/sites-available/extensipedia.backup.$(date +%Y%m%d_%H%M%S)
sudo cp /var/www/extensipedia/backend/.env /var/www/extensipedia/backend/.env.backup.$(date +%Y%m%d_%H%M%S)
sudo cp /var/www/extensipedia/frontend/.env.production /var/www/extensipedia/frontend/.env.production.backup.$(date +%Y%m%d_%H%M%S)
```

#### 20.12.2 Update DNS Management Domainesia untuk `bempefebui.com`

Dari halaman `Managing bempefebui.com` di Domainesia, buka menu `DNS Management`.

Isi record seperti screenshot:

| Host Name | Record Type | Address | Priority |
|---|---|---:|---|
| `bempefebui.com` | `A (Address)` | `187.77.115.15` | `N/A` |
| `www` | `A (Address)` | `187.77.115.15` | `N/A` |

Langkah di panel Domainesia:

1. Login ke Domainesia.
2. Buka `My Domains`.
3. Klik domain `bempefebui.com`.
4. Buka menu `DNS Management`.
5. Pada baris `Host Name` = `bempefebui.com`, pilih `Record Type` = `A (Address)`, isi `Address` = `187.77.115.15`.
6. Pada baris `Host Name` = `www`, pilih `Record Type` = `A (Address)`, isi `Address` = `187.77.115.15`.
7. Biarkan `Priority` kosong atau `N/A`.
8. Klik `Save Changes`.

Catatan:

- Jangan isi `https://bempefebui.com` pada kolom `Address`; DNS A record hanya menerima IP.
- Jangan isi path seperti `/admin/` atau `/api/v1/` di DNS.
- Jika ada record `AAAA` yang tidak dipakai, hapus dulu agar browser tidak mencoba IPv6 yang salah.
- Jika nameserver domain bukan milik Domainesia, edit DNS di provider nameserver aktif, bukan di menu Domainesia.

Tunggu DNS propagate, lalu cek:

```bash
dig +short bempefebui.com
dig +short www.bempefebui.com
nslookup bempefebui.com 1.1.1.1
nslookup www.bempefebui.com 1.1.1.1
```

Expected:

```text
187.77.115.15
```

Jangan lanjut ke Certbot sebelum root domain dan `www` sudah resolve ke IP VPS.

#### 20.12.3 Update Nginx untuk domain baru

Edit config Nginx:

```bash
sudo nano /etc/nginx/sites-available/extensipedia
```

Cari semua baris `server_name`:

```bash
sudo grep -n "server_name" /etc/nginx/sites-available/extensipedia
```

Jika ingin langsung mengganti domain lama dengan domain baru, ubah `server_name` yang semula berisi:

```nginx
server_name extensipedia.com www.extensipedia.com 187.77.115.15;
```

menjadi:

```nginx
server_name bempefebui.com www.bempefebui.com 187.77.115.15;
```

Jika ingin masa transisi agar domain lama masih bisa dibuka sementara, pakai:

```nginx
server_name bempefebui.com www.bempefebui.com extensipedia.com www.extensipedia.com 187.77.115.15;
```

Jika memakai opsi masa transisi dalam satu server block, certificate HTTPS harus mencakup keempat hostname tersebut. Jika tidak, browser bisa menolak `extensipedia.com` karena certificate hanya valid untuk `bempefebui.com`. Untuk migrasi yang lebih rapi, gunakan domain baru sebagai server block utama, lalu buat redirect domain lama pada langkah 20.12.8.

Pastikan routing tetap sama:

```nginx
location ^~ /static/ {
    alias /var/www/extensipedia/backend/staticfiles/;
}

location ^~ /media/ {
    alias /var/www/extensipedia/backend/media/;
}

location ^~ /admin/ {
    proxy_pass http://127.0.0.1:8000;
}

location ^~ /api/v1/ {
    proxy_pass http://127.0.0.1:8000;
}

location ^~ /api/aspirations/ {
    proxy_pass http://127.0.0.1:3000;
}

location / {
    proxy_pass http://127.0.0.1:3000;
}
```

Test dan reload:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Cek HTTP sebelum certificate baru:

```bash
curl -I http://bempefebui.com/
curl -I http://www.bempefebui.com/
```

Expected minimal sudah dijawab oleh Nginx/Next.js. Jika masih timeout atau salah IP, kembali ke DNS.

#### 20.12.4 Buat HTTPS Let's Encrypt untuk `bempefebui.com`

Pastikan Certbot sudah ada:

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

Buat certificate baru:

```bash
sudo certbot --nginx -d bempefebui.com -d www.bempefebui.com
```

Jika pada langkah 20.12.3 kamu sengaja memakai satu server block untuk masa transisi dengan domain lama dan baru sekaligus, buat certificate yang mencakup semuanya:

```bash
sudo certbot --nginx \
  -d bempefebui.com -d www.bempefebui.com \
  -d extensipedia.com -d www.extensipedia.com
```

Jika Certbot bertanya redirect HTTP ke HTTPS, pilih opsi redirect.

Jika Certbot gagal menemukan server block, pastikan `server_name` Nginx sudah memuat `bempefebui.com` dan `www.bempefebui.com`, lalu ulangi:

```bash
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d bempefebui.com -d www.bempefebui.com
```

Cek certificate:

```bash
sudo certbot certificates
sudo certbot renew --dry-run
```

#### 20.12.5 Update environment backend Django

Edit `.env` backend:

```bash
sudo nano /var/www/extensipedia/backend/.env
```

Untuk benar-benar mengganti domain utama ke `bempefebui.com`, ubah menjadi:

```env
DJANGO_ALLOWED_HOSTS=bempefebui.com,www.bempefebui.com,187.77.115.15,localhost,127.0.0.1
DJANGO_CORS_ALLOWED_ORIGINS=
DJANGO_CSRF_TRUSTED_ORIGINS=https://bempefebui.com,https://www.bempefebui.com

DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SECURE_HSTS_SECONDS=31536000
```

Jika `extensipedia.com` masih ingin aktif selama masa transisi, pakai:

```env
DJANGO_ALLOWED_HOSTS=bempefebui.com,www.bempefebui.com,extensipedia.com,www.extensipedia.com,187.77.115.15,localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=https://bempefebui.com,https://www.bempefebui.com,https://extensipedia.com,https://www.extensipedia.com
```

Kunci permission dan restart backend:

```bash
sudo chown extensipedia:www-data /var/www/extensipedia/backend/.env
sudo chmod 600 /var/www/extensipedia/backend/.env
sudo systemctl restart extensipedia-backend
sudo systemctl status extensipedia-backend --no-pager
```

#### 20.12.6 Update environment frontend Next.js

Edit `.env.production` frontend:

```bash
sudo nano /var/www/extensipedia/frontend/.env.production
```

Ubah menjadi:

```env
NEXT_PUBLIC_SITE_URL=https://bempefebui.com
NEXT_PUBLIC_API_BASE_URL=https://bempefebui.com
```

Build ulang karena `NEXT_PUBLIC_*` dibaca saat build:

```bash
cd /var/www/extensipedia/frontend
sudo -Hu extensipedia npm ci
sudo -Hu extensipedia npm run build
sudo systemctl restart extensipedia-frontend
sudo systemctl status extensipedia-frontend --no-pager
```

Reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

#### 20.12.7 Verifikasi domain baru

Cek DNS:

```bash
dig +short bempefebui.com
dig +short www.bempefebui.com
```

Cek HTTPS:

```bash
curl -I https://bempefebui.com/
curl -I https://www.bempefebui.com/
curl -I https://bempefebui.com/akademik
curl -I https://bempefebui.com/kompetensi-karir
curl -I https://bempefebui.com/karir
curl -I https://bempefebui.com/advokasi
curl -I https://bempefebui.com/tentang-kami
curl -I https://bempefebui.com/sitemap.xml
curl -I https://bempefebui.com/admin/
curl https://bempefebui.com/api/v1/
curl https://bempefebui.com/api/v1/public/aspirations/featured/
curl -I "https://bempefebui.com/api/aspirations/track?ticket_id=ASP-XXXXXXXXXX"
```

Cek redirect HTTP ke HTTPS:

```bash
curl -I http://bempefebui.com/
curl -I http://www.bempefebui.com/
```

Expected:

- DNS mengarah ke `187.77.115.15`.
- HTTPS root dan public pages mengembalikan `200 OK`.
- `/admin/` mengembalikan `302 Found` ke login atau halaman admin jika sudah login.
- `/api/v1/` dijawab backend.
- `/api/aspirations/track?...` dijawab Next API route.
- HTTP mengembalikan `301` atau `308` ke HTTPS.

#### 20.12.8 Redirect domain lama ke domain baru

Jika `extensipedia.com` tidak ingin dipakai lagi, arahkan domain lama ke domain baru dari Nginx agar visitor lama tidak putus. Pastikan certificate lama `extensipedia.com` masih ada sebelum membuat redirect HTTPS.

Tambahkan server block terpisah di `/etc/nginx/sites-available/extensipedia`:

```nginx
server {
    listen 80;
    listen 443 ssl;
    server_name extensipedia.com www.extensipedia.com;

    ssl_certificate /etc/letsencrypt/live/extensipedia.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/extensipedia.com/privkey.pem;

    return 301 https://bempefebui.com$request_uri;
}
```

Server block utama aplikasi tetap memakai:

```nginx
server_name bempefebui.com www.bempefebui.com 187.77.115.15;
```

Test dan reload:

```bash
sudo nginx -t
sudo systemctl reload nginx
curl -I https://extensipedia.com/
```

Expected:

```text
HTTP/1.1 301 Moved Permanently
Location: https://bempefebui.com/
```

#### 20.12.9 Troubleshooting khusus `bempefebui.com`

Jika `bempefebui.com` belum membuka VPS:

```bash
dig +short bempefebui.com
dig +short www.bempefebui.com
```

Pastikan:

- `bempefebui.com` dan `www` adalah `A (Address)` ke `187.77.115.15`.
- Nameserver aktif adalah nameserver Domainesia jika DNS dikelola dari panel Domainesia.
- Tidak ada `AAAA` yang mengarah ke IPv6 salah.
- Port `80` dan `443` terbuka.

Jika Certbot gagal:

```bash
sudo nginx -t
sudo grep -R "server_name" -n /etc/nginx/sites-available /etc/nginx/sites-enabled
sudo journalctl -u nginx -n 100 --no-pager
```

Pastikan `server_name` memuat:

```nginx
server_name bempefebui.com www.bempefebui.com 187.77.115.15;
```

Jika admin/API terkena CSRF:

```bash
sudo journalctl -u extensipedia-backend -n 100 --no-pager
```

Pastikan `.env` backend memuat:

```env
DJANGO_ALLOWED_HOSTS=bempefebui.com,www.bempefebui.com,187.77.115.15,localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=https://bempefebui.com,https://www.bempefebui.com
```

Jika sitemap atau link frontend masih memakai `extensipedia.com`, cek `.env.production`, build ulang frontend, lalu restart:

```bash
cat /var/www/extensipedia/frontend/.env.production
cd /var/www/extensipedia/frontend
sudo -Hu extensipedia npm run build
sudo systemctl restart extensipedia-frontend
```
