import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000", // Django
  timeout: 20000,
});

// If you already attach JWT token somewhere, keep that logic.
// Example (only if you store token in localStorage):
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access"); // adjust key if yours differs
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;
