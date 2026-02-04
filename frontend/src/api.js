import axios from 'axios';

const API_BASE_URL = '/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/register', data),
  login: (data) => api.post('/login', data),
  getUser: () => api.get('/user'),
};

// Search API
export const searchAPI = {
  search: (query, tags = []) => {
    const params = new URLSearchParams({ query });
    tags.forEach(tag => params.append('tags[]', tag));
    return api.get(`/search?${params.toString()}`);
  },
};

// Recommendations API
export const recommendationsAPI = {
  get: () => api.get('/recommendations'),
};

// History API
export const historyAPI = {
  get: () => api.get('/history'),
  add: (resourceUrl) => api.post('/history', { resource_url: resourceUrl }),
};

// Admin API
export const adminAPI = {
  getStats: () => api.get('/admin/stats'),
  getResources: (page = 1, perPage = 20) => 
    api.get(`/admin/resources?page=${page}&per_page=${perPage}`),
};

export default api;