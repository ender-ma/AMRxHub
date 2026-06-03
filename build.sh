#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
mkdir -p static staticfiles media

# Use SQLite only for build-time static collection
USE_SQLITE=True python manage.py collectstatic --noinput