import api from '../api'

class NutritionService {
    // Profile endpoints
    async getUserProfile() {
        const response = await api.get('/nutrition/profile/')
        return response.data
    }

    async createOrUpdateProfile(profileData) {
        const response = await api.put('/nutrition/profile/', profileData)
        return response.data
    }

    // Weight record endpoints
    async getWeightRecords() {
        const response = await api.get('/nutrition/weight-records/')
        return response.data
    }

    async addWeightRecord(weightData) {
        const response = await api.post('/nutrition/weight-records/', weightData)
        return response.data
    }

    async updateWeightRecord(id, weightData) {
        const response = await api.put(`/nutrition/weight-records/${id}/`, weightData)
        return response.data
    }

    async deleteWeightRecord(id) {
        const response = await api.delete(`/nutrition/weight-records/${id}/`)
        return response.data
    }

    // Goal endpoints
    async getGoals() {
        const response = await api.get('/nutrition/goals/')
        return response.data
    }

    async createGoal(goalData) {
        const response = await api.post('/nutrition/goals/', goalData)
        return response.data
    }

    async updateGoal(id, goalData) {
        const response = await api.put(`/nutrition/goals/${id}/`, goalData)
        return response.data
    }

    async deleteGoal(id) {
        const response = await api.delete(`/nutrition/goals/${id}/`)
        return response.data
    }

    // Calculation endpoints
    async calculateBMRTDEE(data) {
        const response = await api.post('/nutrition/calculate-bmr-tdee/', data)
        return response.data
    }

    // Analytics endpoints
    async getWeightAnalytics(dateRange = '30d') {
        const response = await api.get(`/nutrition/analytics/?range=${dateRange}`)
        return response.data
    }

    async getDashboardSummary() {
        const response = await api.get('/nutrition/dashboard/')
        return response.data
    }
}

export default new NutritionService() 