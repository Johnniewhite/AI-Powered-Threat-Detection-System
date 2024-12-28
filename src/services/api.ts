import axios from 'axios';

export const api = axios.create({
  baseURL: 'http://localhost:8080',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Detection API
export const detection = {
  getDashboardStats: async () => {
    const response = await api.get('/api/v1/dashboard/stats');
    return response.data;
  },

  getRecentDetections: async () => {
    const response = await api.get('/api/v1/detection/recent');
    return response.data;
  },

  analyzeImage: async (formData: FormData) => {
    const response = await api.post('/api/v1/detection/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  analyzeText: async (text: string) => {
    const response = await api.post('/api/v1/detection/text', { text });
    return response.data;
  },

  getHistory: async () => {
    const response = await api.get('/api/v1/detection/history');
    return response.data;
  },
};

// Users API
export const users = {
  getProfile: async () => {
    const response = await api.get('/api/v1/users/me');
    return response.data;
  },

  updateProfile: async (data: {
    email?: string;
    username?: string;
    current_password?: string;
    new_password?: string;
  }) => {
    const response = await api.put('/api/v1/users/me', data);
    return response.data;
  },
};

export default api; 