#!/usr/bin/env bash
set -euo pipefail

pip install -r requirements.txt
python manage.py collectstatic --noinput

# Set SKIP_MIGRATIONS=1 on Netlify when DB is external/unavailable at build time.
if [ "${SKIP_MIGRATIONS:-1}" != "1" ]; then
  python manage.py migrate --noinput
fi
