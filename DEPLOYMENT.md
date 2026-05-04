# Extensipedia Fullstack Deployment Guide

Panduan ini memasang frontend Next.js dan backend Django pada satu VPS Ubuntu 22.04, dengan routing:

- `http://187.7.115.15/` -> Next.js frontend publik
- `http://187.7.115.15/admin/` -> backend admin dashboard
- `http://187.7.115.15/api/v1/` -> backend API
- `http://187.7.115.15/static/` -> backend static files
- `http://187.7.115.15/media/` -> backend uploaded media

Ganti `187.7.115.15` dengan IP/domain server yang dipakai. Jika sudah punya domain dan TLS, gunakan `https://domain.com` pada environment frontend dan backend.

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
ssh root@187.7.115.15
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

DJANGO_ALLOWED_HOSTS=187.7.115.15,localhost,127.0.0.1
DJANGO_CORS_ALLOWED_ORIGINS=
DJANGO_CSRF_TRUSTED_ORIGINS=http://187.7.115.15

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
DJANGO_ALLOWED_HOSTS=domain.com,www.domain.com,187.7.115.15,localhost,127.0.0.1
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
NEXT_PUBLIC_SITE_URL=http://187.7.115.15
NEXT_PUBLIC_API_BASE_URL=http://187.7.115.15
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
    server_name 187.7.115.15 _;

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
DJANGO_ALLOWED_HOSTS=domain.com,www.domain.com,187.7.115.15,localhost,127.0.0.1
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
curl -I http://187.7.115.15/
curl -I http://187.7.115.15/akademik
curl -I http://187.7.115.15/kompetensi-karir
curl -I http://187.7.115.15/karir
curl -I http://187.7.115.15/advokasi
curl -I http://187.7.115.15/tentang-kami
curl -I http://187.7.115.15/sitemap.xml
curl -I http://187.7.115.15/admin/
curl http://187.7.115.15/api/v1/
curl http://187.7.115.15/api/v1/public/aspirations/featured/
```

Cek bahwa Next API route tetap ke frontend:

```bash
curl -I "http://187.7.115.15/api/aspirations/track?ticket_id=ASP-XXXXXXXXXX"
```

Cek static admin:

```bash
curl -I http://187.7.115.15/static/
```

Cek media jika ada file:

```bash
curl -I http://187.7.115.15/media/path/to/file.jpg
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
curl -X POST http://187.7.115.15/api/v1/public/aspirations/submit/ \
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

- [ ] `http://187.7.115.15/` membuka frontend.
- [ ] `http://187.7.115.15/akademik` membuka halaman akademik.
- [ ] `http://187.7.115.15/kompetensi-karir` membuka halaman kompetensi karir.
- [ ] `http://187.7.115.15/karir` membuka halaman karir.
- [ ] `http://187.7.115.15/advokasi` membuka halaman advokasi.
- [ ] `http://187.7.115.15/tentang-kami` membuka halaman tentang kami.
- [ ] `http://187.7.115.15/sitemap.xml` tidak memakai localhost.
- [ ] `http://187.7.115.15/admin/` membuka backend admin dengan CSS.
- [ ] `http://187.7.115.15/api/v1/` dijawab backend.
- [ ] `http://187.7.115.15/api/v1/public/aspirations/featured/` dijawab backend.
- [ ] `http://187.7.115.15/api/aspirations/track?ticket_id=...` dijawab Next API route.
- [ ] `/static/` diarahkan ke backend staticfiles.
- [ ] `/media/` diarahkan ke backend media.
- [ ] Submit aspirasi mengirim email dan baru mengembalikan `ticket_id` setelah email sukses.
