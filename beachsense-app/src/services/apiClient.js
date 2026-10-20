import axios from "axios";
import { API_BASE_URL } from "../../config";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // first request can be slow while the server fetches ocean data
  headers: { "Content-Type": "application/json" },
});

export default apiClient;
