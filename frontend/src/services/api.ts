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

// Request interceptor to add auth token from Supabase
api.interceptors.request.use(
  async (config) => {
    const session = useAuthStore.getState().session
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`
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
      useAuthStore.getState().signOut()
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

// Competitors API calls
export const competitorsApi = {
  list: (projectId: string) => api.get(`/api/projects/${projectId}/competitors`),

  add: (projectId: string, data: { domain: string; notes?: string }) =>
    api.post(`/api/projects/${projectId}/competitors`, data),

  delete: (projectId: string, competitorId: string) =>
    api.delete(`/api/projects/${projectId}/competitors/${competitorId}`),

  getKeywordOverlap: (projectId: string) =>
    api.get(`/api/projects/${projectId}/competitors/analysis/keyword-overlap`),

  getGapAnalysis: (projectId: string, competitorId: string) =>
    api.get(`/api/projects/${projectId}/competitors/analysis/gap-analysis`, {
      params: { competitor_id: competitorId }
    }),

  getSerpFeatures: (projectId: string) =>
    api.get(`/api/projects/${projectId}/competitors/analysis/serp-features`),
}

// AI Assistant API calls
export const aiApi = {
  chat: (data: {
    message: string
    project_id?: string
    conversation_history?: Array<{ role: string; content: string }>
  }) => api.post('/api/ai/chat', data),

  analyzeKeywords: (projectId: string) =>
    api.post('/api/ai/analyze/keywords', { project_id: projectId }),

  analyzeSERP: (projectId: string, keywordId: string) =>
    api.post('/api/ai/analyze/serp', {
      project_id: projectId,
      keyword_id: keywordId
    }),

  generateContentBrief: (projectId: string, keywordId: string) =>
    api.post('/api/ai/generate/content-brief', {
      project_id: projectId,
      keyword_id: keywordId
    }),
}

// Backlinks API calls
export const backlinksApi = {
  getSummary: (projectId: string) =>
    api.get(`/api/projects/${projectId}/backlinks/summary`),

  getList: (projectId: string, limit?: number, offset?: number) =>
    api.get(`/api/projects/${projectId}/backlinks/list`, {
      params: { limit, offset }
    }),

  getReferringDomains: (projectId: string, limit?: number) =>
    api.get(`/api/projects/${projectId}/backlinks/referring-domains`, {
      params: { limit }
    }),
}

// Webhooks API calls (for n8n integration)
export const webhooksApi = {
  triggerOutreach: (projectId: string, data: {
    webhook_url: string
    competitor_ids?: string[]
    custom_targets?: Array<{ domain: string; email?: string }>
    campaign_name?: string
    include_backlink_data?: boolean
  }) => api.post(`/api/webhooks/outreach/trigger?project_id=${projectId}`, data),

  test: () => api.get('/api/webhooks/test'),
}

export default api
