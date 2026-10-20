# BeachSense - Mobile app (source files)

These are the app's source files. You put them into a **fresh Expo project**, so the Expo version
automatically matches the Expo Go app on your phone.

## 1. Create the Expo project
Install Node.js (LTS) first, then in PowerShell:

```powershell
npx create-expo-app@latest beachsense-app --template blank
cd beachsense-app
npx expo install react-native-maps react-native-gesture-handler react-native-screens react-native-safe-area-context expo-location expo-constants @react-native-async-storage/async-storage
npm install @react-navigation/native @react-navigation/bottom-tabs @react-navigation/native-stack @reduxjs/toolkit react-redux @tanstack/react-query axios
```

## 2. Copy these files into `beachsense-app`
- `App.js`   (replace the existing one)
- `config.js`
- the whole `src` folder

Do NOT copy any package.json / index.js / app.json - the new project already has its own.

## 3. Set the backend address
Open `config.js` and put your laptop's IP in `API_BASE_URL` (`ipconfig` -> IPv4 Address).

## 4. Run
Start the Django backend first (`python manage.py runserver 0.0.0.0:8000`), then:

```powershell
npx expo start
```
Scan the QR code with the Expo Go app (phone and laptop on the same Wi-Fi).

## Problems?
| Problem | Fix |
|---|---|
| Home screen says it can't reach the server | Backend running with `0.0.0.0:8000`? IP in `config.js` correct? Same Wi-Fi? |
| Works on laptop browser, not on phone | Windows Firewall popup for Python -> Allow on private networks |
| "Unable to resolve module ..." | A package from step 1 is missing - run those two install commands again |
