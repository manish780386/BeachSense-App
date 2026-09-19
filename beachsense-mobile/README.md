
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
