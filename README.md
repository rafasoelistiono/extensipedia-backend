# Extensipedia Backend

REST backend for a campus/organization website built with Django, Django REST Framework, PostgreSQL, JWT auth, OpenAPI schema generation, and modular domain apps.

## Local Setup

```bash
python -m venv venv
venv\Scripts\activate
venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env
```

Update `.env` with your local values, especially `DATABASE_URL`, `DJANGO_SECRET_KEY`, and allowed origins.

## Environment Variables

Minimum required:

```env
DJANGO_SECRET_KEY=change-me
DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DJANGO_DEFAULT_FROM_EMAIL=noreply@extensipedia.local
DATABASE_URL=postgresql://postgres:password@127.0.0.1:5432/extensipedia
JWT_ACCESS_TOKEN_MINUTES=15
JWT_REFRESH_TOKEN_DAYS=7
```

## Migrations

```bash
venv\Scripts\python manage.py migrate
```

## Create Superuser

```bash
venv\Scripts\python manage.py createsuperuser
```

## Run Server

```bash
venv\Scripts\python manage.py runserver
```

Useful URLs:

- `http://127.0.0.1:8000/admin/`
- `http://127.0.0.1:8000/admin/login/`
- `http://127.0.0.1:8000/api/v1/`
- `http://127.0.0.1:8000/django-admin/`
- `http://127.0.0.1:8000/api/schema/`
- `http://127.0.0.1:8000/api/schema/swagger-ui/`
- `http://127.0.0.1:8000/api/schema/redoc/`

## Custom Admin Dashboard

The project includes a custom template-based admin dashboard at `/admin/`.

Local development superuser:

```txt
username: superadmin
password: extensipedia.feb.ui
```

This account is created automatically in `DEBUG=True` mode after migrations.
It is for local development only and must be replaced with environment-based or manually managed credentials in production.

If you need to recreate it manually:

```bash
venv\Scripts\python manage.py create_local_superadmin
```

## Run Tests

```bash
venv\Scripts\python manage.py test --settings=config.settings.test
```

## Seed Demo Data

```bash
venv\Scripts\python manage.py seed_demo_data
```

This seeds representative public content, featured aspirations, career resources, competency agenda cards, and 30 days of visitor analytics for dashboard demo use.
