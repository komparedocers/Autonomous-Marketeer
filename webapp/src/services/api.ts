import axios from 'axios'
import { logger } from '../lib/logger'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add auth token and log requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Log request
    logger.debug('API Request', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      params: config.params,
    })

    // Add timestamp for duration calculation
    config.metadata = { startTime: new Date().getTime() }

    return config
  },
  (error) => {
    logger.error('API Request Error', { error: error.message }, error)
    return Promise.reject(error)
  }
)

// Response interceptor - log responses and errors
api.interceptors.response.use(
  (response) => {
    const duration = new Date().getTime() - (response.config.metadata?.startTime || 0)

    logger.debug('API Response', {
      method: response.config.method?.toUpperCase(),
      url: response.config.url,
      status: response.status,
      duration_ms: duration,
      request_id: response.headers['x-request-id'],
    })

    return response
  },
  (error) => {
    const duration = error.config?.metadata?.startTime
      ? new Date().getTime() - error.config.metadata.startTime
      : 0

    logger.error('API Error', {
      method: error.config?.method?.toUpperCase(),
      url: error.config?.url,
      status: error.response?.status,
      statusText: error.response?.statusText,
      errorMessage: error.response?.data?.detail || error.message,
      duration_ms: duration,
      request_id: error.response?.headers['x-request-id'],
    }, error)

    // Handle 401 - redirect to login
    if (error.response?.status === 401) {
      logger.warn('Unauthorized - redirecting to login')
      localStorage.removeItem('token')
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

// Auth
export const login = (email: string, password: string) =>
  api.post('/auth/login', { email, password })

export const register = (data: any) => api.post('/auth/register', data)

// Campaigns
export const getCampaigns = () => api.get('/campaigns')
export const createCampaign = (data: any) => api.post('/campaigns', data)
export const updateCampaign = (id: number, data: any) =>
  api.put(`/campaigns/${id}`, data)
export const deleteCampaign = (id: number) => api.delete(`/campaigns/${id}`)

// Agents
export const getAgentConfigs = () => api.get('/agents/config')
export const runAgent = (data: any) => api.post('/agents/run', data)
export const getAgentRuns = (params?: any) =>
  api.get('/agents/runs', { params })
export const getLLMStatus = () => api.get('/agents/llm/status')

// Analytics
export const getAnalyticsSummary = (params?: any) =>
  axios.get(`${API_URL.replace('8080', '8086')}/summary`, { params })

export const getTimeseries = (params?: any) =>
  axios.get(`${API_URL.replace('8080', '8086')}/timeseries`, { params })

export const getFunnel = (params?: any) =>
  axios.get(`${API_URL.replace('8080', '8086')}/funnel`, { params })

export default api
