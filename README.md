
# BeachSense

This single file covers both the **backend** (`beachsense-backend/`) and the **frontend** (`beachsense-mobile/`) of the BeachSense project.

---

# BeachSense — Backend

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

| Container               | What it does                                                      |
| ----------------------- | ----------------------------------------------------------------- |
| `beach_db`            | PostgreSQL + PostGIS database                                     |
| `beach_redis`         | Redis (Celery broker)                                             |
| `beach_backend`       | Django API server (runs migrations + seeds beaches automatically) |
| `beach_celery_worker` | Executes scheduled background jobs                                |
| `beach_celery_beat`   | Triggers the jobs every 15/30 minutes                             |

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

| Method | Endpoint                                      | Description                                     |
| ------ | --------------------------------------------- | ----------------------------------------------- |
| GET    | `/api/beaches/`                             | List all beaches with latest suitability status |
| GET    | `/api/beaches/{id}/`                        | Beach detail + raw ocean parameters             |
| GET    | `/api/beaches/nearby/?lat=&lng=&radius_km=` | Beaches within radius of a point                |
| POST   | `/api/token/`                               | Obtain JWT access/refresh token                 |
| POST   | `/api/token/refresh/`                       | Refresh JWT access token                        |

## Notes

- `apps/ocean_data/services.py` fetches **real, live data** from the free,
  key-less Open-Meteo Marine and Weather APIs (wave height, wind speed,
  ocean current) for each beach's coordinates. If a query fails or a
  near-shore point falls outside the marine model's grid, it automatically
  falls back to a clearly labelled mock-data generator so the pipeline
  never breaks during a demo.
- Two known gaps are handled transparently rather than silently faked:
  **water quality index** has no free real-time Indian beach-level source
  yet, so it is a labelled placeholder; **tsunami/storm-surge alerts**
  default to inactive pending a stable INCOIS feed or a manual admin
  toggle. Swap these in `apps/ocean_data/services.py` once a source is
  available — nothing else needs to change.
- The suitability formula lives in `apps/suitability/engine.py` — pure
  Python, no Django dependency, easy to unit test and to explain in your
  viva/presentation.
  -e

---

# BeachSense — Mobile App

React Native (Expo, plain JavaScript) app showing real-time recreational
suitability of Indian beaches, backed by the BeachSense Django API.

## Tech Stack

- React Native + Expo (JavaScript, no TypeScript)
- React Navigation (bottom tabs + stack)
- Redux Toolkit (user location state)
- TanStack React Query (API calls, caching, auto-refresh every 5 min)
- react-native-maps (color-coded beach markers)
- expo-location (GPS for nearby-beach alerts)
- expo-notifications (push notifications, wired to backend FCM later)

## Project Structure

```
beachsense-mobile/
├── App.js                     # Providers: Redux, React Query, Navigation
├── app.config.js              # Expo config + API base URL
├── src/
│   ├── screens/
│   │   ├── HomeScreen.js       # List of all beaches + status
│   │   ├── MapScreen.js        # Color-coded map markers
│   │   ├── BeachDetailScreen.js # Live parameters for one beach
│   │   └── AlertsScreen.js     # Nearby beaches currently unsafe
│   ├── components/
│   │   ├── BeachCard.js
│   │   ├── StatusBadge.js
│   │   └── ParameterTile.js
│   ├── navigation/RootNavigator.js
│   ├── redux/                  # store.js + locationSlice.js
│   ├── services/                # apiClient.js, beachApi.js, beachHooks.js
│   ├── constants/theme.js       # colors + suitability status config
│   └── utils/useUserLocation.js
```

## Setup

### 1. Prerequisites

- Node.js 18+
- Expo Go app on your phone (easiest way to test), or an Android/iOS emulator

### 2. Install dependencies

```bash
cd beachsense-mobile
npm install
```

### 3. Point the app at your backend

Open `app.config.js` and set `extra.apiBaseUrl`:

- **Android emulator** → `http://10.0.2.2:8000/api` (already set as default)
- **Physical device (Expo Go)** → use your computer's LAN IP, e.g. `http://192.168.1.5:8000/api`
  (find it with `ipconfig` on Windows or `ifconfig`/`ip a` on Mac/Linux — phone and
  laptop must be on the same Wi-Fi network)
- **iOS simulator** → `http://localhost:8000/api`

### 4. Run the app

```bash
npm start
```

Scan the QR code with Expo Go (Android) or the Camera app (iOS), or press
`a` for Android emulator / `i` for iOS simulator.

## Connecting to the Backend

Make sure the `beachsense-backend` (Django) is running first — either via
`docker compose up` or `python manage.py runserver` — and that
`seed_beaches` has been run so the Home/Map screens have data to show.

## Notes for Guide/Viva

- Screens fetch live data via React Query, which auto-refreshes every 5
  minutes to reflect updated ocean conditions without manual pull-to-refresh.
- Map marker colours and status badges both read from a single shared
  `STATUS_CONFIG` in `src/constants/theme.js`, so SUITABLE/CAUTION/NOT_SUITABLE
  styling stays consistent across every screen.
- `AlertsScreen` requests location permission, then calls the backend's
  `/api/beaches/nearby/` geospatial endpoint to show only beaches within
  15 km that are currently not fully safe.
