import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
  headers: {
    "Content-Type": "app;ication/json",
  },
});

export const fetchReviews = async () => {
  const response = await api.get("/reviews/");
  return response.data;
};

export const triggerTestAudit = async () => {
  const response = await api.post("/reviews/test_audit/");
  return response.data;
};

export default api;
