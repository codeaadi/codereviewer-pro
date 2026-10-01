import axios from 'axios';

// Detect if we are in production or local development
const isProduction = import.meta.env.PROD || window.location.hostname !== 'localhost';

const BASE_URL = isProduction
  ? 'https://codereviewer-pro.onrender.com/api'
  : 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchReviews = async () => {
  const response = await api.get('/reviews/');
  return response.data;
};

export const fetchPullRequests = async () => {
  const response = await api.get('/pull-requests/');
  return response.data;
};

export const triggerTestAudit = async () => {
  const response = await api.post('/reviews/test_audit/');
  return response.data;
};

export default api;
