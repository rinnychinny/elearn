#!/usr/bin/env bash
set -euo pipefail

echo "[start] applying migrations…"
python manage.py migrate --noinput

echo "[start] launching daphne…"
exec daphne -b 0.0.0.0 -p "$PORT" elearn.asgi:application
