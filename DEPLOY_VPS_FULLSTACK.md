# Deploy Full-stack Satu VPS

Panduan ini untuk menjalankan:

- backend Django dari repo ini
- frontend Next.js dari repo sibling `../extensipedia-frontend`
- PostgreSQL lokal di VPS yang sama
- Nginx sebagai reverse proxy tunggal

Target arsitektur:

- `https://domainanda.com/` -> Next.js frontend publik
- `https://domainanda.com/_next/...` -> asset Next.js
- `https://domainanda.com/api/aspirations/...` -> route internal Next.js
- `https://domainanda.com/api/v1/...` -> Django API backend
- `https://domainanda.com/admin/` -> custom admin dashboard Django
- `https://domainanda.com/django-admin/` -> Django admin bawaan
- `https://domainanda.com/static/` -> static file backend
- `https://domainanda.com/media/` -> media file backend

## 1. Struktur Repo yang Diasumsikan

Di mesin lokal Anda sekarang repo berada seperti ini:

```txt
c:\projek\extensipedia-backend
c:\projek\extensipedia-frontend
```

Di VPS, susun serupa agar mudah dikelola:

```txt
/srv/extensipedia/extensipedia-backend
/srv/extensipedia/extensipedia-frontend
```

## 2. Kenapa Routing Ini Penting

Frontend Next.js saat ini memakai:

- `NEXT_PUBLIC_SITE_URL`
- `NEXT_PUBLIC_API_BASE_URL`
- route internal Next di `/api/aspirations/submit`
- route internal Next di `/api/aspirations/track`

Implikasinya:

- jangan proxy semua `/api/` ke Django
- yang diproxy ke Django hanya `/api/v1/`
- route `/api/aspirations/...` harus tetap masuk ke Next.js

## 3. Topologi Port Internal

Gunakan port internal berikut:

- Django gunicorn: `127.0.0.1:8000`
- Next.js: `127.0.0.1:3000`
- PostgreSQL: `127.0.0.1:5432`
- Nginx: `80` dan `443`

## 4. Persiapan VPS Ubuntu

Masuk ke VPS lalu install paket dasar:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip postgresql postgresql-contrib nginx git curl ufw
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

Install Node.js LTS. Untuk Next.js modern, gunakan Node 20 atau versi LTS yang kompatibel:

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs build-essential
node -v
npm -v
```

## 5. Buat User dan Folder Deploy

```bash
sudo adduser --system --group --home /srv/extensipedia extensipedia
sudo mkdir -p /srv/extensipedia
sudo chown -R extensipedia:extensipedia /srv/extensipedia
```

Masuk sebagai user deploy:

```bash
sudo -u extensipedia -H bash
cd /srv/extensipedia
git clone <URL-REPO-BACKEND> extensipedia-backend
git clone <URL-REPO-FRONTEND> extensipedia-frontend
exit
```

## 6. Setup PostgreSQL

```bash
sudo -u postgres psql
```

Jalankan:

```sql
CREATE DATABASE extensipedia;
CREATE USER extensipedia_user WITH PASSWORD 'ganti_password_db_yang_kuat';
GRANT ALL PRIVILEGES ON DATABASE extensipedia TO extensipedia_user;
\q
```

## 7. Setup Backend Django

Masuk sebagai user deploy:

```bash
sudo -u extensipedia -H bash
cd /srv/extensipedia/extensipedia-backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Buat file `.env` production di `/srv/extensipedia/extensipedia-backend/.env`:

```env
DJANGO_SETTINGS_MODULE=config.settings.prod
DJANGO_SECRET_KEY=ganti_dengan_secret_key_panjang
DEBUG=False

DATABASE_URL=postgresql://extensipedia_user:ganti_password_db_yang_kuat@127.0.0.1:5432/extensipedia

DJANGO_ALLOWED_HOSTS=domainanda.com,www.domainanda.com
DJANGO_CORS_ALLOWED_ORIGINS=https://domainanda.com,https://www.domainanda.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://domainanda.com,https://www.domainanda.com

DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SECURE_HSTS_SECONDS=31536000

DJANGO_DEFAULT_FROM_EMAIL=noreply@domainanda.com
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
DJANGO_EMAIL_HOST=smtp.gmail.com
DJANGO_EMAIL_PORT=587
DJANGO_EMAIL_HOST_USER=akun-email-anda
DJANGO_EMAIL_HOST_PASSWORD=app-password-anda
DJANGO_EMAIL_USE_TLS=True
DJANGO_EMAIL_USE_SSL=False
DJANGO_EMAIL_TIMEOUT=30

JWT_ACCESS_TOKEN_MINUTES=15
JWT_REFRESH_TOKEN_DAYS=7
```

Lalu jalankan:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
mkdir -p media
```

Opsional jika ingin isi data contoh:

```bash
python manage.py seed_demo_data
```

Keluar dari shell deploy:

```bash
exit
```

## 8. Setup Frontend Next.js

Masuk lagi sebagai user deploy:

```bash
sudo -u extensipedia -H bash
cd /srv/extensipedia/extensipedia-frontend
npm ci
```

Buat file `.env.production`:

```env
NEXT_PUBLIC_SITE_URL=https://domainanda.com
NEXT_PUBLIC_API_BASE_URL=https://domainanda.com
```

Catatan penting:

- jangan isi `NEXT_PUBLIC_API_BASE_URL` dengan suffix `/api/v1`
- jangan isi dengan `127.0.0.1:8000`
- isi dengan origin publik yang sama agar browser tidak terkena masalah CORS

Build frontend:

```bash
npm run build
exit
```

## 9. Service systemd untuk Backend

Buat file `/etc/systemd/system/extensipedia-backend.service`:

```ini
[Unit]
Description=Extensipedia Django Backend
After=network.target postgresql.service

[Service]
User=extensipedia
Group=www-data
WorkingDirectory=/srv/extensipedia/extensipedia-backend
EnvironmentFile=/srv/extensipedia/extensipedia-backend/.env
ExecStart=/srv/extensipedia/extensipedia-backend/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 120
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Aktifkan service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable extensipedia-backend
sudo systemctl start extensipedia-backend
sudo systemctl status extensipedia-backend
```

## 10. Service systemd untuk Frontend

Buat file `/etc/systemd/system/extensipedia-frontend.service`:

```ini
[Unit]
Description=Extensipedia Next.js Frontend
After=network.target

[Service]
User=extensipedia
Group=www-data
WorkingDirectory=/srv/extensipedia/extensipedia-frontend
Environment=NODE_ENV=production
ExecStart=/usr/bin/npm run start -- --hostname 127.0.0.1 --port 3000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Aktifkan service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable extensipedia-frontend
sudo systemctl start extensipedia-frontend
sudo systemctl status extensipedia-frontend
```

## 11. Konfigurasi Nginx

Buat file `/etc/nginx/sites-available/extensipedia`:

```nginx
server {
    listen 80;
    server_name domainanda.com www.domainanda.com;

    client_max_body_size 20M;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    location /api/v1/ {
        proxy_pass http://127.0.0.1:8000;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
    }

    location /django-admin/ {
        proxy_pass http://127.0.0.1:8000;
    }

    location /static/ {
        proxy_pass http://127.0.0.1:8000;
    }

    location /media/ {
        proxy_pass http://127.0.0.1:8000;
    }

    location /check-api/ {
        proxy_pass http://127.0.0.1:8000;
    }

    location /api/aspirations/ {
        proxy_pass http://127.0.0.1:3000;
    }

    location /_next/ {
        proxy_pass http://127.0.0.1:3000;
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
    }
}
```

Aktifkan site:

```bash
sudo ln -s /etc/nginx/sites-available/extensipedia /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 12. Pasang SSL

Pastikan DNS domain sudah mengarah ke IP VPS.

Install certbot:

```bash
sudo apt install -y certbot python3-certbot-nginx
```

Generate SSL:

```bash
sudo certbot --nginx -d domainanda.com -d www.domainanda.com
```

Setelah SSL aktif, cek lagi apakah file `.env` backend sudah memakai:

- `DJANGO_SECURE_SSL_REDIRECT=True`
- `DJANGO_SESSION_COOKIE_SECURE=True`
- `DJANGO_CSRF_COOKIE_SECURE=True`

Reload service jika Anda mengubah environment:

```bash
sudo systemctl restart extensipedia-backend
sudo systemctl restart extensipedia-frontend
sudo systemctl reload nginx
```

## 13. Mapping URL Final

Hasil akhirnya:

- homepage frontend: `https://domainanda.com/`
- halaman frontend lain: `https://domainanda.com/tentang-kami`, `https://domainanda.com/akademik`, dan seterusnya
- public API backend: `https://domainanda.com/api/v1/public/...`
- admin API backend: `https://domainanda.com/api/v1/admin/...`
- custom admin dashboard backend: `https://domainanda.com/admin/`
- django admin bawaan: `https://domainanda.com/django-admin/`

## 14. Cara Update Deploy Setelah Ada Perubahan

### Backend

```bash
sudo -u extensipedia -H bash
cd /srv/extensipedia/extensipedia-backend
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
exit
sudo systemctl restart extensipedia-backend
```

### Frontend

```bash
sudo -u extensipedia -H bash
cd /srv/extensipedia/extensipedia-frontend
git pull
npm ci
npm run build
exit
sudo systemctl restart extensipedia-frontend
```

## 15. Checklist Verifikasi

Cek service:

```bash
sudo systemctl status extensipedia-backend
sudo systemctl status extensipedia-frontend
sudo systemctl status nginx
```

Cek endpoint backend langsung:

```bash
curl http://127.0.0.1:8000/api/v1/public/core/health/
```

Cek frontend langsung:

```bash
curl http://127.0.0.1:3000
```

Cek domain publik:

```bash
curl https://domainanda.com
curl https://domainanda.com/api/v1/public/core/health/
```

Yang harus berhasil:

- frontend tampil dari `/`
- admin Django tampil dari `/admin/`
- API tampil dari `/api/v1/...`
- media backend tampil
- asset `/_next/` tampil
- form aspiration frontend tetap jalan

## 16. Troubleshooting

### Frontend hidup tapi request API gagal

Cek:

- `NEXT_PUBLIC_API_BASE_URL` harus `https://domainanda.com`
- bukan `127.0.0.1`
- bukan `https://domainanda.com/api/v1`

Lalu rebuild frontend:

```bash
sudo -u extensipedia -H bash
cd /srv/extensipedia/extensipedia-frontend
npm run build
exit
sudo systemctl restart extensipedia-frontend
```

### Route aspirasi frontend rusak

Biasanya karena `/api/` diproxy semua ke Django.

Yang benar:

- `/api/v1/` -> Django
- `/api/aspirations/` -> Next.js

### Admin Django tanpa CSS

Biasanya karena `/static/` tidak diproxy ke backend.

### Image atau attachment tidak muncul

Biasanya karena `/media/` tidak diproxy ke backend.

### Submit aspiration gagal padahal form benar

Cek konfigurasi SMTP backend. Endpoint submit mengirim email konfirmasi secara sinkron.

## 17. Rekomendasi Operasional

- Simpan backend dan frontend dalam repo terpisah tetapi deploy di VPS yang sama
- Gunakan domain utama untuk frontend dan backend agar tidak perlu CORS rumit
- Gunakan subdomain terpisah hanya jika Anda memang ingin memisahkan origin frontend dan backend
- Backup database PostgreSQL secara berkala
- Jika traffic naik, pertimbangkan Redis untuk cache dan analytics visitor yang lebih konsisten

## 18. Akses SSH Berbasis Role

Codebase ini hanya mendefinisikan 4 akun dashboard hardcoded untuk local development:

- `superadmin`
- `akademik`
- `kompetensi`
- `advokasi`

Untuk VPS, akun SSH adalah entitas yang berbeda dari akun dashboard aplikasi. Jangan hardcode password SSH di repo atau menyamakan password aplikasi dengan password Linux.

Rekomendasi pemetaan user SSH:

- `extensipedia` untuk deploy service
- `superadmin` untuk owner teknis penuh
- `akademik` untuk akses operasional akademik bila memang diperlukan
- `kompetensi` untuk akses operasional kompetensi bila memang diperlukan
- `advokasi` untuk akses operasional advokasi bila memang diperlukan

Script bootstrap user tersedia di:

- [ops/create_vps_ssh_users.sh](c:/projek/extensipedia-backend/ops/create_vps_ssh_users.sh)

Cara pakai di VPS sebagai `root`:

```bash
cd /srv/extensipedia/extensipedia-backend
nano ops/create_vps_ssh_users.sh
```

Ganti setiap placeholder `REPLACE_WITH_..._PUBLIC_KEY` dengan public key SSH milik masing-masing user, lalu jalankan:

```bash
chmod +x ops/create_vps_ssh_users.sh
./ops/create_vps_ssh_users.sh
```

Verifikasi:

```bash
id extensipedia
id superadmin
id akademik
id kompetensi
id advokasi
```

Catatan:

- script hanya memberi grup `sudo` ke user `extensipedia`
- akun role lain dibuat tanpa password dan ditujukan untuk login via SSH key
- jika Anda tetap ingin password login Linux, set manual setelah user dibuat dengan `passwd <username>`, tetapi ini bukan rekomendasi utama
