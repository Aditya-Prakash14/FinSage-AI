import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const financeAPI = {
  /**
   * Generate income/expense forecast
   */
  async generateForecast(userId, forecastDays = 7, includeConfidence = true) {
    const response = await apiClient.post('/api/finance/forecast', {
      user_id: userId,
      forecast_days: forecastDays,
      include_confidence: includeConfidence,
    });
    return response.data;
  },

  /**
   * Get AI-powered financial insights
   */
  async getInsights(userId, context = null) {
    const response = await apiClient.post('/api/finance/insights', {
      user_id: userId,
      context,
    });
    return response.data;
  },

  /**
   * Optimize budget using RL agent
   */
  async optimizeBudget(userId, targetSavingsRate = 0.15, riskTolerance = 'medium') {
    const response = await apiClient.post('/api/finance/budget/optimize', {
      user_id: userId,
      target_savings_rate: targetSavingsRate,
      risk_tolerance: riskTolerance,
    });
    return response.data;
  },

  /**
   * Upload transactions
   */
  async uploadTransactions(userId, transactions) {
    const response = await apiClient.post('/api/finance/transactions/batch', {
      transactions,
    }, {
      params: { user_id: userId }
    });
    return response.data;
  },

  /**
   * Get user transactions
   */
  async getTransactions(userId, days = 30) {
    const response = await apiClient.get('/api/finance/transactions', {
      params: { user_id: userId, days }
    });
    return response.data;
  },

  /**
   * Detect spending anomalies
   */
  async getAnomalies(userId) {
    const response = await apiClient.get('/api/finance/anomalies', {
      params: { user_id: userId }
    });
    return response.data;
  },

  /**
   * Submit feedback on recommendations
   */
  async submitFeedback(actionId, feedback, userId) {
    const response = await apiClient.post('/api/feedback/update', {
      action_id: actionId,
      feedback,  // 'like' or 'dislike'
      user_id: userId,
    });
    return response.data;
  },

  /**
   * Health check
   */
  async healthCheck() {
    const response = await apiClient.get('/api/finance/health');
    return response.data;
  },
};

export default apiClient;
