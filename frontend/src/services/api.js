import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  logout: () => api.post('/auth/logout'),
};

// Admin API
export const adminAPI = {
  // Users
  listUsers: () => api.get('/admin/users'),
  createUser: (userData) => api.post('/admin/users', userData),
  updateUser: (userId, userData) => api.put(`/admin/users/${userId}`, userData),
  deleteUser: (userId) => api.delete(`/admin/users/${userId}`),
  
  // Settings
  getSettings: () => api.get('/admin/settings'),
  updateSettings: (settings) => api.put('/admin/settings', settings),
};

// Platforms API
export const platformsAPI = {
  list: () => api.get('/platforms'),
  create: (platformData) => api.post('/platforms', platformData),
  delete: (platformId) => api.delete(`/platforms/${platformId}`),
};

// Dealers API
export const dealersAPI = {
  list: () => api.get('/dealers'),
  get: (dealerId) => api.get(`/dealers/${dealerId}`),
  create: (dealerData) => api.post('/dealers', dealerData),
  update: (dealerId, dealerData) => api.put(`/dealers/${dealerId}`, dealerData),
  delete: (dealerId) => api.delete(`/dealers/${dealerId}`),
  addCompetitor: (dealerId, competitorData) => 
    api.post(`/dealers/${dealerId}/competitors`, competitorData),
  deleteCompetitor: (competitorId) => 
    api.delete(`/dealers/competitors/${competitorId}`),
};

// Vehicles API
export const vehiclesAPI = {
  getDealerVehicles: (dealerId, params) => 
    api.get(`/vehicles/dealer/${dealerId}`, { params }),
  getCompetitorVehicles: (competitorId, params) => 
    api.get(`/vehicles/competitor/${competitorId}`, { params }),
  getDealerStats: (dealerId, params) => 
    api.get(`/vehicles/stats/dealer/${dealerId}`, { params }),
};

// Scraping API
export const scrapeAPI = {
  triggerScrape: (dealerId, includeCompetitors = true) => 
    api.post(`/scrape/dealer/${dealerId}?include_competitors=${includeCompetitors}`),
  getJobStatus: (jobId) => api.get(`/scrape/status/${jobId}`),
  getRecentJobs: (dealerId) => api.get(`/scrape/dealer/${dealerId}/recent`),
};

export default api;
