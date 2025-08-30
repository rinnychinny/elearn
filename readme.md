# Elearn

Async Django application for e‑learning with PostgreSQL, Redis, Celery, and optional AWS S3 storage.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Repository Layout](#repository-layout)
- [Prerequisites](#prerequisites)
- [Quick Start (Local)](#quick-start-local)
- [Environment Variables](#environment-variables)
- [Running the App](#running-the-app)
- [Background Tasks (Celery)](#background-tasks-celery)
- [Testing](#testing)
- [Common Issues](#common-issues)
- [Deployment Notes](#deployment-notes)

## Overview
Elearn is an asynchronous Django project that powers an e‑learning platform. It uses **ASGI** (via Daphne) for real‑time features, **Celery** for background jobs, **Redis** for brokering and caching, and **PostgreSQL** for persistence. Media files can be stored locally or in AWS S3 depending on configuration.

## Features
- User accounts & auth (`accounts/`)
- REST API endpoints (`api/`)
- Real‑time chat / messaging (`chat/`)
- Courses & course materials (`courses/`, `course_materials/`)
- Background task processing with Celery (workers + beat)
- Configurable storage: local or AWS S3
- Production scripts (`render-start.sh`, `postgres_init.sql`)

## Tech Stack
- Python 3.11+
- Django (ASGI‑capable)
- Django Channels (for WebSocket/chat)
- **Daphne** (ASGI server)
- PostgreSQL 14+
- Redis 6+
- Celery 5+
- AWS S3 (optional, for media)
- Django REST Framework

> Exact versions are pinned in `requirements.txt`.

## Repository Layout
```
accounts/
api/
chat/
course_materials/
courses/
elearn/
manage.py
postgres_init.sql
render-start.sh
requirements.txt
pytest.ini
```

## Prerequisites
- Python 3.11+
- PostgreSQL 14+ (local or managed)
- Redis 6+
- `virtualenv` or `pyenv`

## Quick Start (Local)
```bash
# Clone
git clone https://github.com/rinnychinny/elearn.git
cd elearn

# Virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
Create .env file with the sample variables and insert correct values for your environment.

# Setup postgres DB
# run this script with postgres superuser
# elearn_db and elearn _app creation and priveleges
sudo -u postgres psql -f ./postgres_init.sql

# Some Django DB setup - migrations/superuser/user groups
python manage.py migrate
python manage.py createsuperuser
python manage.py users_init #django user group and user initialisation

# Ensure Redis and Postgres running locally

# Run app (ASGI)
python manage.py runserver
 or
daphne -b 0.0.0.0 -p 8000 elearn.asgi:application

# Visit http://localhost:8000
```

## Environment Variables
A `.env` is recommended with the following fields:

```dotenv
# Django
SECRET_KEY=changeme
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000
DJANGO_SETTINGS_MODULE=elearn.settings

# Database
DATABASE_URL=postgres://elearn_app:elearn_app@localhost:5432/elearn_db

# Redis
REDIS_URL=redis://127.0.0.1:6379/0

# Celery
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}

# Storage
USE_S3=0   # set to 1 to enable AWS S3 storage

# AWS S3 (only used if USE_S3=1)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=elearn-media-bucket
AWS_S3_REGION_NAME=eu-north-1
```

## Running the App
Run with Daphne:
```bash
daphne -b 0.0.0.0 -p 8000 elearn.asgi:application
```

## Background Tasks (Celery)
```bash
celery -A elearn worker -l info
```

## Testing
```bash
pytest -q
```

## Common Issues
- Ensure Postgres/Redis are running.
- If using AWS S3 (`USE_S3=1`), confirm your AWS credentials and bucket exist.
- CSRF errors may require updating `CSRF_TRUSTED_ORIGINS`.

## Deployment Notes
- Use **Daphne** behind a reverse proxy (e.g., Nginx).
- Set `USE_S3=1` and configure AWS credentials to use S3 for media storage.
- Run migrations automatically on deploy.
- Run Celery worker and beat as services or sidecars.
- For Render: use `render-start.sh` for the web service, and add a separate background worker service for Celery.
- Always set `DEBUG=0` in production and configure `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` accordingly.


