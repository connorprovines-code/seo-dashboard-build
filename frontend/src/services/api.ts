import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth state on 401 Unauthorized
      useAuthStore.getState().clearAuth()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API calls
export const authApi = {
  register: (email: string, password: string) =>
    api.post('/api/auth/register', { email, password }),

  login: (email: string, password: string) =>
    api.post('/api/auth/login', new URLSearchParams({ username: email, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),

  getCurrentUser: () => api.get('/api/auth/me'),

  refreshToken: () => api.post('/api/auth/refresh'),
}

// Projects API calls
export const projectsApi = {
  list: () => api.get('/api/projects'),

  get: (id: string) => api.get(`/api/projects/${id}`),

  create: (data: { name: string; domain: string }) =>
    api.post('/api/projects', data),

  update: (id: string, data: { name?: string; domain?: string }) =>
    api.put(`/api/projects/${id}`, data),

  delete: (id: string) => api.delete(`/api/projects/${id}`),
}

// API Credentials
export const credentialsApi = {
  check: (provider: string) => api.get(`/api/credentials/check/${provider}`),

  setup: (provider: string, credentials: any) =>
    api.post(`/api/credentials/setup/${provider}`, credentials),

  get: (provider: string) => api.get(`/api/credentials/${provider}`),

  delete: (provider: string) => api.delete(`/api/credentials/${provider}`),
}

// Keywords API calls
export const keywordsApi = {
  list: (projectId: string) => api.get(`/api/projects/${projectId}/keywords`),

  get: (projectId: string, keywordId: string) =>
    api.get(`/api/projects/${projectId}/keywords/${keywordId}`),

  add: (projectId: string, keyword: string) =>
    api.post(`/api/projects/${projectId}/keywords`, { keyword_text: keyword }),

  bulkAdd: (projectId: string, keywords: string[]) =>
    api.post(`/api/projects/${projectId}/keywords/bulk`, { keywords }),

  refresh: (projectId: string, keywordId: string) =>
    api.put(`/api/projects/${projectId}/keywords/${keywordId}/refresh`),

  refreshAll: (projectId: string) =>
    api.post(`/api/projects/${projectId}/keywords/refresh-all`),

  estimateCost: (projectId: string) =>
    api.get(`/api/projects/${projectId}/keywords/cost-estimate/refresh`),

  delete: (projectId: string, keywordId: string) =>
    api.delete(`/api/projects/${projectId}/keywords/${keywordId}`),
}

// Rank Tracking API calls
export const rankTrackingApi = {
  list: (projectId: string) => api.get(`/api/projects/${projectId}/rank-tracking`),

  enable: (projectId: string, data: {
    keyword_id: string
    tracked_url: string
    location_code?: number
    language_code?: string
  }) => api.post(`/api/projects/${projectId}/rank-tracking`, data),

  getHistory: (projectId: string, keywordId: string, days?: number) =>
    api.get(`/api/projects/${projectId}/rank-tracking/${keywordId}/history`, {
      params: { days }
    }),

  getSerp: (projectId: string, keywordId: string) =>
    api.get(`/api/projects/${projectId}/rank-tracking/${keywordId}/serp`),

  checkNow: (projectId: string, keywordId: string) =>
    api.post(`/api/projects/${projectId}/rank-tracking/${keywordId}/check-now`),

  stop: (projectId: string, keywordId: string) =>
    api.delete(`/api/projects/${projectId}/rank-tracking/${keywordId}`),

  getStats: (projectId: string) =>
    api.get(`/api/projects/${projectId}/rank-tracking/stats/overview`),
}

export default api
