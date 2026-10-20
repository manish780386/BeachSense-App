# BeachSense — Backend

## Quick start on your laptop (no Docker, no PostgreSQL, no GDAL)

```bash
python -m venv venv
venv\Scripts\activate            # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_beaches       # loads 20 Indian beaches
python manage.py refresh_ocean_data # fetches live data + computes status (needs internet)
python manage.py runserver 0.0.0.0:8000
```

Check: http://127.0.0.1:8000/api/beaches/  ·  Swagger: http://127.0.0.1:8000/api/docs/

SQLite is the default database. Celery/Redis are NOT needed to run the API; without them the
ocean data is not refreshed automatically, so run `python manage.py refresh_ocean_data` whenever
you want fresh data. (Docker + PostgreSQL + Celery setup is described further below and is optional.)

---

Django + DRF backend for BeachSense — a mobile app that shows real-time recreational suitability of Indian beaches.
Fetches ocean/weather data, computes a SUITABLE / CAUTION / NOT_SUITABLE
status per beach, exposes it via REST APIs, and sends location-based push
alerts to nearby users.

## Tech Stack
- Django 5 + Django REST Framework
- PostgreSQL + PostGIS (geospatial queries)
- Celery + Redis (scheduled INCOIS data fetch & alerting)
- JWT auth (SimpleJWT)
- drf-spectacular (Swagger docs at `/api/docs/`)

## Project Structure
```
beachsense-backend/
├── apps/
│   ├── beaches/         # Beach model, API, nearby-search, admin, seed command
│   ├── ocean_data/       # OceanParameter model, INCOIS fetch service, Celery task
│   ├── suitability/      # Scoring engine + SuitabilityStatus model + Celery task
│   ├── users/             # Custom User model (FCM token, last known location)
│   └── notifications/     # AlertLog model, FCM push service, alert Celery task
├── core/                   # settings.py, urls.py, wsgi.py
├── celery_app/             # Celery app + beat schedule (every 30/15 min)
├── seed_data/beaches.csv   # 20 major Indian beaches to seed the DB
├── requirements.txt
├── .env.example
└── manage.py
```

## 🐳 Quickest Start — Docker (Recommended)

No need to install Python, PostgreSQL, PostGIS or Redis manually — Docker runs everything for you in isolated containers.

### Prerequisites
- Docker + Docker Compose installed

### Steps
```bash
cd beachsense-backend
cp .env.example .env
# Open .env and change DB_HOST=localhost to DB_HOST=db   (Docker service name)

docker compose up --build
```

This single command starts **5 containers**:
| Container | What it does |
|---|---|
| `beach_db` | PostgreSQL + PostGIS database |
| `beach_redis` | Redis (Celery broker) |
| `beach_backend` | Django API server (runs migrations + seeds beaches automatically) |
| `beach_celery_worker` | Executes scheduled background jobs |
| `beach_celery_beat` | Triggers the jobs every 15/30 minutes |

Once running:
- API: http://localhost:8000/api/beaches/
- Swagger docs: http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/ (create a superuser with `docker compose exec backend python manage.py createsuperuser`)

Stop everything: `docker compose down` (add `-v` to also wipe the database volume).

## ⚙️ CI/CD — GitHub Actions

`.github/workflows/backend-ci.yml` runs automatically on every push/PR to
`main` or `dev`. It spins up Postgres+PostGIS and Redis as service
containers, then:
1. Installs dependencies
2. Runs `python manage.py check` (catches config errors)
3. Verifies no missing migrations, then applies them
4. Builds the Docker image

If any step fails, the PR shows a red cross on GitHub — this is what a real
team uses to make sure nobody merges broken code.

**Recommended branch strategy** (mention this to your guide too):
- `main` — always stable, deployable code
- `dev` — integration branch, everyone merges here first
- `feature/xyz` — one branch per feature (e.g. `feature/suitability-engine`), merged into `dev` via Pull Request

## Local Setup (Manual, without Docker)

### 1. Prerequisites
- Python 3.11+
- PostgreSQL with PostGIS extension
- Redis

### 2. Install PostgreSQL + PostGIS (Ubuntu example)
```bash
sudo apt install postgresql postgresql-contrib postgis
sudo -u postgres psql
CREATE DATABASE beachsense_db;
\c beachsense_db
CREATE EXTENSION postgis;
\q
```

### 3. Python environment
```bash
cd beachsense-backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in your local DB/Redis values
```

### 4. Migrate & seed
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_beaches   # loads seed_data/beaches.csv
```

### 5. Run the API server
```bash
python manage.py runserver
```
- Swagger docs: http://127.0.0.1:8000/api/docs/
- Admin panel: http://127.0.0.1:8000/admin/
- Beaches API: http://127.0.0.1:8000/api/beaches/
- Nearby search: http://127.0.0.1:8000/api/beaches/nearby/?lat=15.54&lng=73.75&radius_km=15

### 6. Run Celery (separate terminals, Redis must be running)
```bash
celery -A core worker -l info
celery -A core beat -l info
```
Together these two automatically fetch ocean data every 30 min, compute
suitability, and send alerts every 15 min — no manual triggering needed
once running.

## Key API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/beaches/` | List all beaches with latest suitability status |
| GET | `/api/beaches/{id}/` | Beach detail + raw ocean parameters |
| GET | `/api/beaches/nearby/?lat=&lng=&radius_km=` | Beaches within radius of a point |
| POST | `/api/token/` | Obtain JWT access/refresh token |
| POST | `/api/token/refresh/` | Refresh JWT access token |

## Notes
- `apps/ocean_data/services.py` currently returns **mock data** — swap
  `fetch_reading_for_beach()` with a real INCOIS API call/scraper once
  access is confirmed with your guide. Nothing else needs to change.
- The suitability formula lives in `apps/suitability/engine.py` — pure
  Python, no Django dependency, easy to unit test and to explain in your
  viva/presentation.
