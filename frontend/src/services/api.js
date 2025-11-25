import axios from "axios";

// Use '/api' in dev to leverage Vite proxy; allow override via VITE_API_URL
const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const uploadAMCFile = (formData) =>
  api.post("/portfolio/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

export const createPortfolio = (data) => api.post("/portfolio", data);

export const getPortfolio = (id) => api.get(`/portfolio/${id}`);

export const refreshPortfolio = (id) => api.get(`/portfolio/${id}/refresh`);

export const loginUser  = (credentials) => api.post("/auth/login", credentials);

export const registerUser  = (data) => api.post("/auth/register", data);

export default api;