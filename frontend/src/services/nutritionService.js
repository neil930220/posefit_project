import api from './api'

class NutritionService {
    // Profile endpoints
    async getUserProfile() {
        const response = await api.get('api/nutrition/profile/')
        return response.data
    }

    async createOrUpdateProfile(profileData) {
        const response = await api.put('api/nutrition/profile/', profileData)
        return response.data
    }

    // Weight record endpoints
    async getWeightRecords() {
        console.log('Making weight records request to:', api.defaults.baseURL + 'api/nutrition/weight-records/');
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

    async createGoal(goalData) {
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

    // Calculation endpoints
    async calculateBMRTDEE(data) {
        const response = await api.post('api/nutrition/calculate-bmr-tdee/', data)
        return response.data
    }

    // Analytics endpoints
    async getWeightAnalytics(dateRange = 'week') {
        try {
            console.log('Fetching weight analytics with dateRange:', dateRange);
            const response = await api.get(`api/nutrition/analytics/?range=${dateRange}`);
            
            // Log the response for debugging
            console.log('Weight analytics response:', {
                status: response.status,
                headers: response.headers,
                data: response.data
            });

            // Validate response format
            if (!response.data || typeof response.data !== 'object') {
                throw new Error(`Invalid response format from analytics endpoint: ${JSON.stringify(response.data)}`);
            }

            return response.data;
        } catch (error) {
            console.error('Error fetching weight analytics:', {
                message: error.message,
                response: error.response?.data,
                status: error.response?.status,
                headers: error.response?.headers
            });
            
            // Return a default structure in case of error
            return {
                analytics: {
                    current_weight: null,
                    starting_weight: null,
                    weight_change: null
                },
                chart_data: {
                    dates: [],
                    weights: [],
                    bmr: [],
                    tdee: []
                },
                goal_progress: null,
                date_range: dateRange
            };
        }
    }

    async getDashboardSummary() {
        const response = await api.get('api/nutrition/dashboard/')
        return response.data
    }
}

export default new NutritionService() 