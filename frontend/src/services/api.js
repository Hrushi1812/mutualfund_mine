import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
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