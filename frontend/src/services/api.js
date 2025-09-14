import axios from "axios";

// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

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