import axios from 'axios';

// Configuration de base pour axios
const API_BASE_URL = 'https://promotion-app-backend.onrender.com';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
} );

// Intercepteur pour ajouter le token d'authentification
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les erreurs de réponse
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expiré ou invalide
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API d'authentification
export const authAPI = {
  login: async (credentials) => {
    const response = await api.post('/api/auth/login', credentials);
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/api/auth/logout');
    return response.data;
  },
};

// API des campagnes
export const campaignAPI = {
  getCampaigns: async () => {
    const response = await api.get('/api/campaigns/');
    return response.data;
  },

  getCampaign: async (id) => {
    const response = await api.get(`/api/campaigns/${id}`);
    return response.data;
  },

  createCampaign: async (campaignData) => {
    const response = await api.post('/api/campaigns/', campaignData);
    return response.data;
  },

  updateCampaign: async (id, campaignData) => {
    const response = await api.put(`/api/campaigns/${id}`, campaignData);
    return response.data;
  },

  deleteCampaign: async (id) => {
    const response = await api.delete(`/api/campaigns/${id}`);
    return response.data;
  },

  getCampaignStats: async (id) => {
    const response = await api.get(`/api/campaigns/${id}/stats`);
    return response.data;
  },
};

// API des données promotionnelles
export const promotionDataAPI = {
  getPromotionData: async () => {
    const response = await api.get('/api/promotion-data/');
    return response.data;
  },

  getPromotionDataItem: async (id) => {
    const response = await api.get(`/api/promotion-data/${id}`);
    return response.data;
  },

  createPromotionData: async (data) => {
    const response = await api.post('/api/promotion-data/', data);
    return response.data;
  },

  updatePromotionData: async (id, data) => {
    const response = await api.put(`/api/promotion-data/${id}`, data);
    return response.data;
  },

  deletePromotionData: async (id) => {
    const response = await api.delete(`/api/promotion-data/${id}`);
    return response.data;
  },

  getPromotionDataByCampaign: async (campaignId) => {
    const response = await api.get(`/api/promotion-data/campaign/${campaignId}`);
    return response.data;
  },
};

// API des utilisateurs
export const userAPI = {
  getUsers: async () => {
    const response = await api.get('/api/users/');
    return response.data;
  },

  getUser: async (id) => {
    const response = await api.get(`/api/users/${id}`);
    return response.data;
  },

  updateUser: async (id, userData) => {
    const response = await api.put(`/api/users/${id}`, userData);
    return response.data;
  },

  deleteUser: async (id) => {
    const response = await api.delete(`/api/users/${id}`);
    return response.data;
  },

  getPromotrices: async () => {
    const response = await api.get('/api/users/promotrices');
    return response.data;
  },

  getUserStats: async () => {
    const response = await api.get('/api/users/stats');
    return response.data;
  },
};

export default api;
