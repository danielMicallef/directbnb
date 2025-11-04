# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DirectBnB is a property rental platform built with Django and PostgreSQL/PostGIS. The project uses Docker Compose with Traefik as a reverse proxy for local development with HTTPS.

## Architecture

### Backend Structure

The Django backend is located in `backend/src/` with the following key components:

- **Core module** (`backend/src/core/`): Django project settings, URLs, WSGI/ASGI configuration
  - `settings.py`: Main Django settings with PostGIS database configuration and optional S3/Cloudflare R2 storage
  - `models.py`: Contains `AbstractTrackedModel` base class for models with automatic `created_at`/`updated_at` tracking

- **Apps** (`backend/src/apps/`):
  - `users`: Custom user model (`BNBUser`) using email as username with phone number and avatar support
  - `properties`: Property listings (currently minimal model structure)

- **Custom User Model**: `AUTH_USER_MODEL = "users.BNBUser"` - uses email authentication instead of username

### Infrastructure

- **Database**: PostGIS (PostgreSQL with GIS extensions) v17-3.5 on port 5432
- **Web Server**: Gunicorn running Django on port 8000 internally, exposed on 8001
- **Reverse Proxy**: Traefik v3.5.4 handling HTTPS termination with self-signed certificates
- **Package Management**: UV (modern Python package manager) with `pyproject.toml`

### Docker Networks

- `db_network`: Bridge network connecting app and database
- `web_network`: Bridge network connecting app and Traefik

## Development Commands

### Initial Setup

1. Generate self-signed certificates for local HTTPS:
```bash
mkdir -p certs && openssl req -x509 -nodes -newkey rsa:2048 -keyout certs/local-cert.key -out certs/local-cert.crt -subj "/CN=localhost"
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Build and start all services:
```bash
docker compose up -d --build
```

### Running Django Commands

Execute Django management commands inside the app container:
```bash
docker compose exec app uv run python manage.py <command>
```

Common examples:
```bash
# Run migrations
docker compose exec app uv run python manage.py migrate

# Create superuser
docker compose exec app uv run python manage.py createsuperuser

# Run Django shell
docker compose exec app uv run python manage.py shell

# Collect static files
docker compose exec app uv run python manage.py collectstatic
```

### Database Management

```bash
# Access PostgreSQL shell
docker compose exec db psql -U postgresuser -d postgres

# Run migrations
docker compose exec app uv run python manage.py migrate

# Create new migrations
docker compose exec app uv run python manage.py makemigrations
```

### Linting and Formatting

The project uses Ruff for linting and formatting (dev dependency):
```bash
# Inside the backend directory or container
uv run ruff check .
uv run ruff format .
```

### Logs and Debugging

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f app
docker compose logs -f db
docker compose logs -f traefik

# Access app container shell
docker compose exec app bash
```

### Rebuilding

```bash
# Rebuild and restart services
docker compose up -d --build

# Rebuild specific service
docker compose up -d --build app

# Stop and remove containers
docker compose down

# Stop and remove containers with volumes (data loss)
docker compose down -v
```

## Environment Configuration

Key environment variables (see `.env.example`):

- `DEBUG`: Enable Django debug mode (True/False)
- `DJANGO_SECRET_KEY`: Django secret key for production
- `POSTGRES_*`: Database credentials and connection details
- `USE_S3`: Enable Cloudflare R2/S3 storage (True/False)
- `AWS_*`: S3/R2 storage credentials when `USE_S3=True`

## Storage Backend

The project supports two storage backends:

1. **Local FileSystem** (default): Files stored in Django's media directory
2. **Cloudflare R2/S3**: Set `USE_S3=True` and configure AWS credentials

The storage backend is configured in `backend/src/core/settings.py` lines 118-146.

## Access Points

- **Django App**: https://localhost (via Traefik) or http://localhost:8001 (direct)
- **Traefik Dashboard**: http://localhost:8080
- **Django Admin**: https://localhost/admin
- **PostgreSQL**: localhost:5432

## Important Notes

- The Django settings have a hardcoded `SECRET_KEY` at `backend/src/core/settings.py:24` that should be replaced with the environment variable in production
- There's a typo in `settings.py:93` where `POSTGRES_PASSWORD` is used instead of `POSTGRES_HOST` for the database HOST setting
- The project uses Python 3.13 (specified in `pyproject.toml` and Dockerfile)
- PostGIS database backend is used: `django.contrib.gis.db.backends.postgis`
- Models should inherit from `AbstractTrackedModel` (from `core.models`) to get automatic timestamp tracking