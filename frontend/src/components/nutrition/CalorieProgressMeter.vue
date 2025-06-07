<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-900">Calorie Progress</h3>
      
      <!-- Controls -->
      <div class="flex space-x-2">
        <!-- Comparison Type Toggle -->
        <div class="flex bg-gray-100 rounded-lg p-1">
          <button
            @click="comparisonType = 'bmr'"
            :class="[
              'px-3 py-1 text-sm font-medium rounded-md transition-colors',
              comparisonType === 'bmr' 
                ? 'bg-white text-blue-600 shadow-sm' 
                : 'text-gray-500 hover:text-gray-700'
            ]"
          >
            BMR
          </button>
          <button
            @click="comparisonType = 'tdee'"
            :class="[
              'px-3 py-1 text-sm font-medium rounded-md transition-colors',
              comparisonType === 'tdee' 
                ? 'bg-white text-blue-600 shadow-sm' 
                : 'text-gray-500 hover:text-gray-700'
            ]"
          >
            TDEE
          </button>
        </div>

        <!-- Date Range Selector -->
        <select
          v-model="dateRange"
          class="text-sm border border-gray-300 rounded-md px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="1d">Today</option>
          <option value="7d">7 Days</option>
          <option value="30d">30 Days</option>
          <option value="90d">90 Days</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-8">
      <div class="text-red-600 mb-2">{{ error }}</div>
      <button
        @click="loadData"
        class="text-blue-600 hover:text-blue-800 text-sm font-medium"
      >
        Try Again
      </button>
    </div>

    <!-- Content -->
    <div v-else-if="data">
      <!-- Overall Progress Circle -->
      <div class="flex items-center justify-center mb-6">
        <div class="relative w-32 h-32">
          <svg class="w-32 h-32 transform -rotate-90" viewBox="0 0 100 100">
            <!-- Background circle -->
            <circle
              cx="50"
              cy="50"
              r="42"
              stroke="#e5e7eb"
              stroke-width="8"
              fill="none"
            />
            <!-- Progress circle -->
            <circle
              cx="50"
              cy="50"
              r="42"
              :stroke="getProgressColor(data.analytics.overall_progress_percentage)"
              stroke-width="8"
              fill="none"
              stroke-linecap="round"
              :stroke-dasharray="264"
              :stroke-dashoffset="264 - (264 * Math.min(data.analytics.overall_progress_percentage, 100) / 100)"
              class="transition-all duration-1000 ease-out"
            />
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <div class="text-2xl font-bold text-gray-900">
              {{ Math.round(data.analytics.overall_progress_percentage) }}%
            </div>
            <div class="text-sm text-gray-500">Average</div>
          </div>
        </div>
      </div>

      <!-- Statistics -->
      <div class="grid grid-cols-2 gap-4 mb-6">
        <div class="text-center p-3 bg-gray-50 rounded-lg">
          <div class="text-2xl font-semibold text-gray-900">
            {{ Math.round(data.analytics.avg_daily_intake) }}
          </div>
          <div class="text-sm text-gray-500">Avg Daily Intake</div>
          <div class="text-xs text-gray-400">kcal</div>
        </div>
        <div class="text-center p-3 bg-gray-50 rounded-lg">
          <div class="text-2xl font-semibold text-gray-900">
            {{ Math.round(data.analytics.target_calories) }}
          </div>
          <div class="text-sm text-gray-500">Target {{ comparisonType.toUpperCase() }}</div>
          <div class="text-xs text-gray-400">kcal</div>
        </div>
      </div>

      <!-- Day Status Summary -->
      <div class="grid grid-cols-3 gap-2 mb-4">
        <div class="text-center p-2 bg-green-50 rounded">
          <div class="text-lg font-semibold text-green-600">
            {{ data.analytics.days_on_target }}
          </div>
          <div class="text-xs text-green-600">On Target</div>
        </div>
        <div class="text-center p-2 bg-yellow-50 rounded">
          <div class="text-lg font-semibold text-yellow-600">
            {{ data.analytics.days_under_target }}
          </div>
          <div class="text-xs text-yellow-600">Under</div>
        </div>
        <div class="text-center p-2 bg-red-50 rounded">
          <div class="text-lg font-semibold text-red-600">
            {{ data.analytics.days_over_target }}
          </div>
          <div class="text-xs text-red-600">Over</div>
        </div>
      </div>

      <!-- Streak Information -->
      <div class="flex justify-between items-center p-3 bg-blue-50 rounded-lg mb-4">
        <div class="text-center">
          <div class="text-lg font-semibold text-blue-600">
            {{ data.analytics.current_streak }}
          </div>
          <div class="text-xs text-blue-600">Current Streak</div>
        </div>
        <div class="text-center">
          <div class="text-lg font-semibold text-blue-600">
            {{ data.analytics.best_streak }}
          </div>
          <div class="text-xs text-blue-600">Best Streak</div>
        </div>
      </div>

      <!-- Daily Progress Bars -->
      <div v-if="dateRange !== '1d'" class="space-y-2">
        <h4 class="text-sm font-medium text-gray-700 mb-2">Daily Progress</h4>
        <div class="space-y-1 max-h-40 overflow-y-auto">
          <div
            v-for="day in data.daily_data.slice(-10)"
            :key="day.date"
            class="flex items-center space-x-3 text-sm"
          >
            <div class="w-16 text-gray-500">
              {{ formatDate(day.date) }}
            </div>
            <div class="flex-1 bg-gray-200 rounded-full h-2">
              <div
                :class="[
                  'h-2 rounded-full transition-all duration-500',
                  getProgressColor(day.progress_percentage, true)
                ]"
                :style="{ width: Math.min(day.progress_percentage, 100) + '%' }"
              ></div>
            </div>
            <div class="w-12 text-xs text-gray-600">
              {{ Math.round(day.progress_percentage) }}%
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import nutritionService from '../../services/nutritionService'

export default {
  name: 'CalorieProgressMeter',
  setup() {
    const data = ref(null)
    const loading = ref(false)
    const error = ref('')
    const dateRange = ref('7d')
    const comparisonType = ref('tdee')

    const loadData = async () => {
      try {
        loading.value = true
        error.value = ''
        data.value = await nutritionService.getCalorieProgress(dateRange.value, comparisonType.value)
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to load calorie progress data'
        console.error('Error loading calorie progress:', err)
      } finally {
        loading.value = false
      }
    }

    const getProgressColor = (percentage, isBackground = false) => {
      if (percentage >= 90 && percentage <= 110) {
        return isBackground ? 'bg-green-500' : '#10b981'
      } else if (percentage < 90) {
        return isBackground ? 'bg-yellow-500' : '#f59e0b'
      } else {
        return isBackground ? 'bg-red-500' : '#ef4444'
      }
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      })
    }

    // Watch for changes in controls
    watch([dateRange, comparisonType], loadData)

    onMounted(loadData)

    return {
      data,
      loading,
      error,
      dateRange,
      comparisonType,
      loadData,
      getProgressColor,
      formatDate
    }
  }
}
</script>

<style scoped>
/* Custom scrollbar for daily progress */
.space-y-1::-webkit-scrollbar {
  width: 4px;
}

.space-y-1::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 2px;
}

.space-y-1::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}

.space-y-1::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style> 