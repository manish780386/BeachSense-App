export default {
  expo: {
    name: "BeachSense",
    slug: "beachsense",
    version: "1.0.0",
    orientation: "portrait",
    icon: "./assets/icon.png",
    userInterfaceStyle: "light",
    splash: {
      backgroundColor: "#065A82",
    },
    android: {
      package: "com.beachsense.app",
      permissions: ["ACCESS_FINE_LOCATION", "ACCESS_COARSE_LOCATION"],
      // Place the file you downloaded from Firebase Console > Project Settings
      // > General > Your apps (Android) right here in the project root.
      // Required for push notifications (FCM) to work on Android.
      googleServicesFile: "./google-services.json",
    },
    ios: {
      bundleIdentifier: "com.beachsense.app",
      supportsTablet: true,
    },
    plugins: ["expo-notifications"],
    extra: {
      // Point this at your Django backend — use your machine's LAN IP
      // when testing on a physical device (localhost won't work on-device).
      apiBaseUrl: "http://10.0.2.2:8000/api",
    },
  },
};