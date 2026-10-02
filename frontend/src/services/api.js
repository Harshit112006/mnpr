import axios from "axios";


const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";


const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});


export const checkBackendHealth =
  async () => {
    const response =
      await api.get(
        "/api/health"
      );

    return response.data;
  };


export const analyzeAnimalImage =
  async (file) => {
    const formData =
      new FormData();

    formData.append(
      "image",
      file
    );

    const response =
      await api.post(
        "/api/detect",
        formData
      );

    return response.data;
  };


export default api;