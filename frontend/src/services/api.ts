import axios from 'axios';
import { PropertyRequest, PropertyResponse, CMAHistory } from '../types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // Ensure headers object exists
      if (!config.headers) {
        config.headers = {};
      }
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

export const cmaApi = {
  analyzeCMA: async (data: PropertyRequest): Promise<PropertyResponse> => {
    const response = await api.post('/cma/analyze', data);
    return response.data as PropertyResponse;
  },

  getCMAHistory: async (): Promise<CMAHistory[]> => {
    const response = await api.get('/cma/history');
    return response.data as CMAHistory[];
  },

  downloadPDFReport: async (analysisId: number): Promise<Blob> => {
    const response = await api.get(`/cma/report/${analysisId}`, {
      responseType: 'blob',
    });
    return response.data as Blob;
  },

  healthCheck: async (): Promise<{ status: string; timestamp: string }> => {
    const response = await api.get('/health');
    return response.data as { status: string; timestamp: string };
  },
}; 