# Olympiad Error Atlas

Private web app for Olympiad math training. Track every attempt, log mistakes, schedule spaced reviews, and surface analytics so patterns never repeat.

## Features
- Authentication with per-user data isolation.
- Problems, attempts with time tracking, and mistake taxonomy.
- Review queue with Again/Hard/Good/Easy grading (SM-2 style scheduler).
- Mistake analytics: topic balance, recurring types, trend over time.
- Import/export JSON for backups and migrations.
- Django admin pre-configured.

## Tech stack
- Python 3.12, Django 5, SQLite (default)
- Bootstrap 5 + HTMX (lightweight interactions)
- Chart.js for analytics, Whitenoise for static files, Gunicorn for production

## Local development
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
# adjust DEBUG/SECRET_KEY/etc as needed
python manage.py migrate
python manage.py runserver
```

Run tests:
```bash
pytest
```

## Settings
- Development: `config.settings.dev` (default in `manage.py`).
- Production: `config.settings.prod`.
- Key env vars: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DATABASE_URL`, `DJANGO_SETTINGS_MODULE`, `RENDER_DEPLOY_HOOK_URL` (CI).

## Deployment on Render (free tier)
1. Push this repo to GitHub.
2. Create a **Render Web Service** from the repo.
3. Environment:
   - `PYTHON_VERSION=3.12`
   - `DJANGO_SETTINGS_MODULE=config.settings.prod`
   - `SECRET_KEY=<generate>`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=<your-render-url>`
   - `CSRF_TRUSTED_ORIGINS=https://<your-render-url>`
   - `DATABASE_URL=sqlite:////var/data/db.sqlite3` (use Render Disk for persistence)  
     > Without a disk, SQLite will reset on each deploy because Render’s filesystem is ephemeral.
4. Add a **Render Disk** (e.g., 1GB at `/var/data`) so SQLite survives deploys; free tier supports this on Web Services.
5. Build command:
   ```bash
   pip install -r requirements.txt
   python manage.py collectstatic --noinput --settings=config.settings.prod
   python manage.py migrate --settings=config.settings.prod
   ```
6. Start command:
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
   ```

### Deploy hooks + GitHub Actions
- In Render, create a **Deploy Hook** for the service and store the URL in GitHub Secrets as `RENDER_DEPLOY_HOOK_URL`.
- GitHub Actions workflow (`.github/workflows/ci.yml`):
  - Runs on PRs and pushes to `main`.
  - Installs dependencies, runs `pytest`.
  - On successful push to `main`, hits the deploy hook to trigger a Render deploy.

## Import/Export
- Export: `Export` button in the nav downloads your data as JSON.
- Import: `Import` button accepts a JSON export and recreates problems, attempts, mistakes, and reviews for the logged-in user.

## Notes on data persistence
- SQLite is the default. With Render’s ephemeral filesystem, data resets on deploy unless you mount a persistent disk. For multi-user or heavier workloads, point `DATABASE_URL` to a managed Postgres instance (Render offers a free Postgres tier) without code changes.

## Docker (optional)
Build and run locally:
```bash
docker build -t olympiad-error-atlas .
docker run -p 8000:8000 --env-file .env olympiad-error-atlas
```
