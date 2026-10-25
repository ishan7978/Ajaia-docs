#!/usr/bin/env bash
# Render build step: install deps and collect static files.
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
