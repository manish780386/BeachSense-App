# Beach Recreational Suitability — Backend

Django + DRF backend for the Beach Recreational Suitability mobile app.
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
beach-safety-backend/
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

## Local Setup

### 1. Prerequisites

- Python 3.11+
- PostgreSQL with PostGIS extension
- Redis

### 2. Install PostgreSQL + PostGIS (Ubuntu example)

```bash
sudo apt install postgresql postgresql-contrib postgis
sudo -u postgres psql
CREATE DATABASE beach_safety_db;
\c beach_safety_db
CREATE EXTENSION postgis;
\q
```

### 3. Python environment

```bash
cd beach-safety-backend
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

| Method | Endpoint                                      | Description                                     |
| ------ | --------------------------------------------- | ----------------------------------------------- |
| GET    | `/api/beaches/`                             | List all beaches with latest suitability status |
| GET    | `/api/beaches/{id}/`                        | Beach detail + raw ocean parameters             |
| GET    | `/api/beaches/nearby/?lat=&lng=&radius_km=` | Beaches within radius of a point                |
| POST   | `/api/token/`                               | Obtain JWT access/refresh token                 |
| POST   | `/api/token/refresh/`                       | Refresh JWT access token                        |

## Notes

- `apps/ocean_data/services.py` currently returns **mock data** — swap
  `fetch_reading_for_beach()` with a real INCOIS API call/scraper once
  access is confirmed with your guide. Nothing else needs to change.
- The suitability formula lives in `apps/suitability/engine.py` — pure
  Python, no Django dependency, easy to unit test and to explain in your
  viva/presentation.
