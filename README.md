
# Django Image Studio (scaffold)
A ready-to-run Django app for image upload and manipulations.
Features added: drag-and-drop upload with progress, extra filters (sepia, vignette, polaroid), version history, user accounts (Django auth), admin registration, Dockerfile & Procfile.

## Quick start

1. Create and activate a virtualenv

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run migrations and start server

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

3. Open http://127.0.0.1:8000
