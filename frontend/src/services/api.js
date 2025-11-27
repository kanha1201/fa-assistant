import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const apiService = {
  async getSummary(companySymbol) {
    const response = await api.get(`/summary`, {
      params: { company_symbol: companySymbol },
    })
    return response.data
  },

  async getRedFlags(companySymbol) {
    const response = await api.get(`/red-flags`, {
      params: { company_symbol: companySymbol },
    })
    return response.data
  },

  async getBullBear(companySymbol) {
    const response = await api.get(`/bull-bear`, {
      params: { company_symbol: companySymbol },
    })
    return response.data
  },

  async answerQuery(companySymbol, query) {
    const response = await api.get(`/chat/query`, {
      params: {
        company_symbol: companySymbol,
        query: query,
      },
    })
    return response.data
  },
}


