import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

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
