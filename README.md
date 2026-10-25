# BeachSense

**Recreational suitability information for beaches across India.**
BeachSense tells a tourist, in one glance, whether a beach is **Suitable**, needs **Caution**, or is **Not suitable** right now, using live wave, wind and ocean-current data, and warns them when a beach near their location turns unsafe.

> Final-year project - Shri Vaishnav Institute of Information Technology (SVVV, Indore)
> Department of Information Security & Cloud Computing - Guide: **Prof. Vishwas Dixit**
> Team: Manish Dange, Harsh Shukla, Naman Jain, Gaurav Upadhyay

---

## Contents

1. [What it does](#1-what-it-does)
2. [How a beach is judged](#2-how-a-beach-is-judged)
3. [Data sources and honest limitations](#3-data-sources-and-honest-limitations)
4. [Architecture](#4-architecture)
5. [Tech stack](#5-tech-stack)
6. [Project structure](#6-project-structure)
7. [Getting started](#7-getting-started)
8. [API reference](#8-api-reference)
9. [Running the tests](#9-running-the-tests)
10. [Optional extras](#10-optional-extras)
11. [Troubleshooting](#11-troubleshooting)
12. [Roadmap](#12-roadmap)

---

## 1. What it does

| Feature                                                                             | Status                                        |
| ----------------------------------------------------------------------------------- | --------------------------------------------- |
| 20 major beaches across 10 coastal states / UTs, stored with latitude and longitude | Working                                       |
| Live wave height, wind speed and ocean-current data per beach (Open-Meteo)          | Working                                       |
| Suitability score and Suitable / Caution / Not suitable status per beach            | Working                                       |
| Colour-coded **list** and **map** (green / amber / red)                 | Working                                       |
| Beach detail screen with all live parameters and active hazard alerts               | Working                                       |
| **Nearby alerts**: beaches within 15 km of the user that are not fully safe   | Working                                       |
| REST API with interactive Swagger documentation                                     | Working                                       |
| Auto-refresh every 5 minutes in the app                                             | Working                                       |
| Scheduled data refresh (Celery + Redis)                                             | Optional, implemented                         |
| Push notifications (Firebase)                                                       | Partly implemented, see [Roadmap](#12-roadmap) |

### App screens

- **Home** - every beach with its status badge, pull down to refresh
- **Map** - India map with a coloured marker per beach, tap a marker for details
- **Beach detail** - score, wave height, wind, current, water quality, active alerts
- **Alerts** - beaches near your location that need caution

---

## 2. How a beach is judged

The scoring engine (`beachsense-backend/apps/suitability/engine.py`) is a small pure-Python function, easy to test and explain.

```
Score = 100 - min(15 x Wave, 40) - min(0.5 x Wind, 20) - min(2 x Current, 20) - 0.2 x (100 - WaterQuality)

Wave = wave height (m)   Wind = wind speed (km/h)   Current = current speed (km/h)   WaterQuality = 0..100
```

| Score      | Status                 |
| ---------- | ---------------------- |
| 70 or more | **Suitable**     |
| 40 to 69.9 | **Caution**      |
| below 40   | **Not suitable** |

- A **tsunami** or **storm-surge** alert forces `Not suitable` (score 0) regardless of the other values.
- Every deduction is **capped**, so one extreme number cannot dominate the result.

Worked example: wave 1.8 m, wind 30 km/h, current 3 km/h, water quality 100 -> `100 - 27 - 15 - 6 = 52` -> **Caution**.

---

## 3. Data sources and honest limitations

| Parameter                    | Source                           | Status                                                                                           |
| ---------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------------ |
| Wave height                  | Open-Meteo **Marine** API  | Live (forecast model)                                                                            |
| Ocean current speed          | Open-Meteo **Marine** API  | Live (unit is read from the API response)                                                        |
| Wind speed                   | Open-Meteo **Weather** API | Live                                                                                             |
| Water quality                | -                                | **Simulated placeholder.** No free real-time beach-level source exists for India           |
| Tsunami / storm-surge alerts | -                                | Flags exist in the data model but there is **no live feed** yet (INCOIS has no public API) |

Please keep these in mind:

- Wave, wind and current values come from a **global forecast model**, not from sensors on the beach. Treat them as guidance, never as a replacement for lifeguards and local warning flags.
- If the live request fails (for example no internet), the backend falls back to generated demo values and labels those readings `MOCK_FALLBACK` in the database, so they are never silently mixed with real data.
- Replacing Open-Meteo with official **INCOIS** data is the main planned improvement once institutional access is available.

---

## 4. Architecture

```
                 +----------------------------+
                 |  Open-Meteo Marine/Weather |
                 +-------------+--------------+
                               | live data (HTTPS)
                               v
+------------------+   REST   +-----------------------------+   +--------------------+
|  Mobile app      | <------> |  Django REST API            |-->|  SQLite (default)  |
|  React Native    |   JSON   |  beaches | ocean_data |     |   |  or PostgreSQL     |
|  (Expo)          |          |  suitability | users |      |   +--------------------+
+------------------+          |  notifications              |
                              +--------------+--------------+
                                             |  optional
                              Celery + Redis (scheduled refresh)  .  Firebase (push)
```

Two flows:

1. **Background pipeline** - fetch Open-Meteo data -> store `OceanParameter` -> scoring engine -> store `SuitabilityStatus`.
2. **User request** - app calls `GET /api/beaches/` -> API returns each beach with its latest status -> app draws list / map.

---

## 5. Tech stack

| Layer      | Technology                                                                                                                      |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Mobile app | React Native (Expo, JavaScript), React Navigation, Redux Toolkit, TanStack React Query, Axios, react-native-maps, expo-location |
| Backend    | Python, Django, Django REST Framework, SimpleJWT, drf-spectacular (Swagger), django-cors-headers                                |
| Data       | SQLite (default), PostgreSQL (optional), Open-Meteo APIs, Haversine distance                                                    |
| Optional   | Celery + Redis, Firebase Admin SDK, Docker, GitHub Actions                                                                      |

---

## 6. Project structure

```
BeachSense/
|-- beachsense-backend/
|   |-- manage.py
|   |-- requirements.txt            everything needed to run locally
|   |-- requirements-extra.txt      only for Docker / PostgreSQL / push notifications
|   |-- core/                       settings, urls, wsgi
|   |-- celery_app/                 optional scheduler (Celery Beat)
|   |-- seed_data/beaches.csv       20 beaches
|   `-- apps/
|       |-- beaches/                Beach model, API, nearby search (Haversine), seed command
|       |-- ocean_data/             OceanParameter model, Open-Meteo fetching, refresh command
|       |-- suitability/            scoring engine, status model, automated tests
|       |-- users/                  custom user model
|       `-- notifications/          alert log, Firebase service, alert task
`-- beachsense-app/
    |-- App.js
    |-- config.js                   <- put your backend address here
    `-- src/
        |-- screens/                Home, Map, BeachDetail, Alerts
        |-- components/             BeachCard, StatusBadge, ParameterTile
        |-- navigation/             tabs + stack
        |-- services/               API client, React Query hooks
        |-- redux/                  user-location state
        |-- constants/theme.js      colours and status styles
        `-- utils/                  location hook
```

---

## 7. Getting started

You need: **Python 3.11+**, **Node.js (LTS)**, and the **Expo Go** app on an Android/iOS phone.
No Docker, PostgreSQL, Redis or GDAL is needed to run the project.

### 7.1 Backend (Windows PowerShell)

```powershell
cd beachsense-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_beaches            # loads the 20 beaches
python manage.py refresh_ocean_data      # fetches live data + computes status (30-60 s, needs internet)
python manage.py runserver 0.0.0.0:8000
```

Check it in the browser:

- API: http://127.0.0.1:8000/api/beaches/
- Swagger: http://127.0.0.1:8000/api/docs/
- Admin (optional, run `python manage.py createsuperuser` first): http://127.0.0.1:8000/admin/

> Always start the server with `0.0.0.0:8000`. Plain `runserver` is reachable only from the laptop itself, not from your phone.
> Without Celery the data is not refreshed automatically - run `python manage.py refresh_ocean_data` whenever you want fresh values.

### 7.2 Mobile app

Create a fresh Expo project so its version matches the Expo Go app on your phone:

```powershell
npx create-expo-app@latest beachsense-app --template blank
cd beachsense-app
npx expo install react-native-maps react-native-gesture-handler react-native-screens react-native-safe-area-context expo-location expo-constants @expo/vector-icons @react-native-async-storage/async-storage
npm install @react-navigation/native @react-navigation/bottom-tabs @react-navigation/native-stack @reduxjs/toolkit react-redux @tanstack/react-query axios
```

Copy `App.js`, `config.js` and the `src/` folder into the project (replace the existing `App.js`).

Open `config.js` and set your laptop's address (run `ipconfig`, copy the **IPv4 Address**):

```js
export const API_BASE_URL = "http://192.168.1.10:8000/api";   // keep /api at the end
```

Start the app (backend must be running):

```powershell
npx expo start
```

Scan the QR code with Expo Go. The phone and the laptop must be on the **same Wi-Fi**.
Android emulator: use `http://10.0.2.2:8000/api`. iOS simulator: `http://localhost:8000/api`.

---

## 8. API reference

Base URL: `http://<your-ip>:8000/api`. Read endpoints are public.

| Method | Endpoint                                              | Description                                                    |
| ------ | ----------------------------------------------------- | -------------------------------------------------------------- |
| GET    | `/beaches/`                                         | All beaches with their latest status                           |
| GET    | `/beaches/{id}/`                                    | One beach, including the latest raw ocean parameters           |
| GET    | `/beaches/nearby/?lat=15.55&lng=73.75&radius_km=15` | Beaches within the radius, nearest first, with `distance_km` |
| POST   | `/token/`                                           | Get a JWT access / refresh token                               |
| POST   | `/token/refresh/`                                   | Refresh an access token                                        |
| GET    | `/docs/`                                            | Interactive Swagger UI                                         |
| GET    | `/schema/`                                          | OpenAPI schema                                                 |

Example - `GET /api/beaches/nearby/?lat=15.55&lng=73.75&radius_km=10`

```json
[
  {
    "id": 2,
    "name": "Baga Beach",
    "state": "Goa",
    "district": "North Goa",
    "latitude": 15.5553,
    "longitude": 73.7517,
    "distance_km": 0.62,
    "current_status": { "status": "CAUTION", "score": 58.0, "computed_at": "2026-10-20T11:18:05Z" },
    "is_active": true
  }
]
```

`GET /api/beaches/{id}/` adds a `parameters` object: `wave_height_m`, `wind_speed_kmph`, `current_speed_kmph`, `water_quality_index`, `tsunami_alert`, `storm_surge_alert`, `high_wave_alert`, `recorded_at`.
`current_status` is `null` for a beach that has no data yet (this is normal, not an error).

---

## 9. Running the tests

```powershell
cd beachsense-backend
python manage.py test
```

20 automated tests:

- **Scoring engine (11)** - calm / moderate / rough conditions, both hazard overrides, the 70 and 40 score boundaries, deduction caps, water-quality effect
- **Data pipeline (3)** - one reading stored per beach, status computed from the latest reading, inactive beaches skipped
- **REST API (6)** - list, detail, nearby (radius and ordering), missing parameters rejected, unknown beach returns 404, Swagger served

---

## 10. Optional extras

**Scheduled refresh (Celery + Redis).** `celery_app/celery.py` schedules: fetch ocean data every 30 min, compute status at :05 and :35, check user alerts every 15 min. Needs a Redis server and the packages in `requirements-extra.txt`.

**Docker + PostgreSQL.** `docker-compose.yml` starts PostgreSQL, Redis, the API, a Celery worker and Celery Beat. Set `DB_ENGINE=postgres` in `.env` (copy `.env.example`). Not required for local development.

**Firebase push notifications.** The backend can send pushes through the Firebase Admin SDK. Save the service-account key as `beachsense-backend/secrets/firebase-service-account.json` (the folder is git-ignored; never commit this file) and install `firebase-admin`.

---

## 11. Troubleshooting

| Problem                                                             | Fix                                                                                                                                                                                                                                  |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Could not find the GDAL library`                                 | You are on an old copy. This project no longer uses GeoDjango/GDAL - re-download the latest backend                                                                                                                                  |
| `Application labels aren't unique`                                | Two apps share a name. Check each `apps/*/apps.py` has its own `name = "apps.<folder>"`                                                                                                                                          |
| App shows loading forever / cannot reach server                     | Server running with `0.0.0.0:8000`? Correct IP in `config.js`? Phone on the same Wi-Fi?                                                                                                                                          |
| Browser on the phone cannot open `http://<ip>:8000/api/beaches/`  | Allow port 8000 in Windows Firewall (PowerShell as admin): `New-NetFirewallRule -DisplayName "Django 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow`, and set the Wi-Fi network profile to **Private** |
| `Unable to resolve module @expo/vector-icons` (or another module) | Install it: `npx expo install @expo/vector-icons`, then restart with `npx expo start -c`                                                                                                                                         |
| `Project is incompatible with this version of Expo Go`            | Create a fresh project with `npx create-expo-app@latest` instead of reusing an old `package.json`                                                                                                                                |
| Home screen is empty                                                | Run `python manage.py seed_beaches` then `python manage.py refresh_ocean_data`                                                                                                                                                   |
| Beaches show no status                                              | Run `python manage.py refresh_ocean_data` (computes the status)                                                                                                                                                                    |

---

## 12. Roadmap

- Official **INCOIS** data for waves, currents and hazard alerts
- A real water-quality data source
- End-to-end **push notifications**: register device tokens and locations from the app, deliver through Firebase
- Hourly **forecast** ("safe window today") and **activity-wise** suitability (swimming, surfing, boating)
- Admin control to switch hazard alerts on/off, plus an alert history
- Crowd-sourced beach reports and an SOS button that shares live location
- Dashboard for tourism boards and disaster-management authorities
- Cloud deployment and a release APK

---

## Acknowledgements

Wave, wind and current data: [Open-Meteo](https://open-meteo.com). Background and motivation: India's Draft Blue Economy Policy and the ocean-state services of INCOIS (Ministry of Earth Sciences).
