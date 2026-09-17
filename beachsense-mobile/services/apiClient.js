import axios from "axios";
import Constants from "expo-constants";

const API_BASE_URL = Constants.expoConfig?.extra?.apiBaseUrl || "http://10.0.2.2:8000/api";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT token automatically once auth is added
apiClient.interceptors.request.use(async (config) => {
  // const token = await AsyncStorage.getItem("access_token");
  // if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default apiClient;