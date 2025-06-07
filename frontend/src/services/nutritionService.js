import api from './api'

class NutritionService {
    // Profile endpoints
    async getUserProfile() {
        const response = await api.get('api/nutrition/profile/')
        return response.data
    }

    async updateUserProfile(profileData) {
        const response = await api.put('api/nutrition/profile/', profileData)
        return response.data
    }

    // Weight record endpoints
    async getWeightRecords() {
        const response = await api.get('api/nutrition/weight-records/')
        return response.data
    }

    async addWeightRecord(weightData) {
        const response = await api.post('api/nutrition/weight-records/', weightData)
        return response.data
    }

    async updateWeightRecord(id, weightData) {
        const response = await api.put(`api/nutrition/weight-records/${id}/`, weightData)
        return response.data
    }

    async deleteWeightRecord(id) {
        const response = await api.delete(`api/nutrition/weight-records/${id}/`)
        return response.data
    }

    // Goal endpoints
    async getGoals() {
        const response = await api.get('api/nutrition/goals/')
        return response.data
    }

    async addGoal(goalData) {
        const response = await api.post('api/nutrition/goals/', goalData)
        return response.data
    }

    async updateGoal(id, goalData) {
        const response = await api.put(`api/nutrition/goals/${id}/`, goalData)
        return response.data
    }

    async deleteGoal(id) {
        const response = await api.delete(`api/nutrition/goals/${id}/`)
        return response.data
    }

    // Analytics endpoints
    async getWeightAnalytics(dateRange = '30d') {
        const response = await api.get(`api/nutrition/analytics/?range=${dateRange}`)
        return response.data
    }

    async getCalorieProgress(dateRange = '7d', comparisonType = 'tdee') {
        const response = await api.get(`api/nutrition/calorie-progress/?range=${dateRange}&type=${comparisonType}`)
        return response.data
    }

    async getDashboardSummary() {
        const response = await api.get('api/nutrition/dashboard/')
        return response.data
    }

    // Calculation endpoints
    async calculateBMRTDEE(data) {
        const response = await api.post('api/nutrition/calculate-bmr-tdee/', data)
        return response.data
    }
}

export default new NutritionService() 