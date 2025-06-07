<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">營養健康管理系統</h1>
        <p class="mt-2 text-gray-600">追蹤您的基礎代謝率（BMR）、每日消耗總熱量（TDEE）和體重目標</p>
      </div>

      <!-- Quick Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-sm font-medium text-gray-500">目前體重</h3>
          <p class="text-2xl font-bold text-gray-900">
            {{ dashboardData?.latest_weight?.weight || '--' }} kg
          </p>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-sm font-medium text-gray-500">基礎代謝率 (BMR)</h3>
          <p class="text-2xl font-bold text-blue-600">
            {{ dashboardData?.profile?.bmr || '--' }} kcal
          </p>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-sm font-medium text-gray-500">每日消耗總熱量 (TDEE)</h3>
          <p class="text-2xl font-bold text-green-600">
            {{ dashboardData?.profile?.tdee || '--' }} kcal
          </p>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-sm font-medium text-gray-500">目標進度</h3>
          <p class="text-2xl font-bold text-purple-600">
            {{ dashboardData?.current_goal?.progress_percentage || '--' }}%
          </p>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left Column -->
        <div class="lg:col-span-2 space-y-8">
          <!-- Profile Setup -->
          <div v-if="!hasProfile" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-yellow-800">請先完成個人資料設定</h3>
                <p class="mt-1 text-sm text-yellow-700">為了計算準確的BMR和TDEE，請填寫您的基本資料。</p>
                <button @click="showProfileModal = true" class="mt-2 bg-yellow-600 text-white px-4 py-2 rounded-md text-sm hover:bg-yellow-700">
                  設定個人資料
                </button>
              </div>
            </div>
          </div>

          <!-- BMR/TDEE Calculator -->
          <div class="bg-white rounded-lg shadow">
            <div class="px-6 py-4 border-b border-gray-200">
              <h2 class="text-lg font-medium text-gray-900">BMR / TDEE 計算器</h2>
            </div>
            <div class="p-6">
              <BMRCalculator @calculated="handleBMRCalculated" />
            </div>
          </div>

          <!-- Calorie Progress Meter -->
          <CalorieProgressMeter />
        </div>

        <!-- Right Column -->
        <div class="space-y-8">
          <!-- Quick Actions -->
          <div class="bg-white rounded-lg shadow">
            <div class="px-6 py-4 border-b border-gray-200">
              <h2 class="text-lg font-medium text-gray-900">快速操作</h2>
            </div>
            <div class="p-6 space-y-3">
              <button @click="showWeightModal = true" class="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                記錄體重
              </button>
              <button @click="showGoalModal = true" class="w-full bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700">
                設定目標
              </button>
              <button @click="showProfileModal = true" class="w-full bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700">
                編輯個人資料
              </button>
            </div>
          </div>

          <!-- Goal Progress -->
          <div v-if="dashboardData?.current_goal" class="bg-white rounded-lg shadow">
            <div class="px-6 py-4 border-b border-gray-200">
              <h2 class="text-lg font-medium text-gray-900">目標進度</h2>
            </div>
            <div class="p-6">
              <GoalProgress :goal="dashboardData.current_goal" />
            </div>
          </div>

          <!-- Recent Weight Records -->
          <div class="bg-white rounded-lg shadow">
            <div class="px-6 py-4 border-b border-gray-200">
              <h2 class="text-lg font-medium text-gray-900">最近記錄</h2>
            </div>
            <div class="p-6">
              <RecentWeightRecords @refresh="loadDashboard" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <ProfileModal 
      v-if="showProfileModal" 
      @close="showProfileModal = false" 
      @saved="handleProfileSaved"
    />
    
    <WeightModal 
      v-if="showWeightModal" 
      @close="showWeightModal = false" 
      @saved="handleWeightSaved"
    />
    
    <GoalModal 
      v-if="showGoalModal" 
      @close="showGoalModal = false" 
      @saved="handleGoalSaved"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import nutritionService from '../services/nutritionService'
import BMRCalculator from '../components/nutrition/BMRCalculator.vue'
import GoalProgress from '../components/nutrition/GoalProgress.vue'
import RecentWeightRecords from '../components/nutrition/RecentWeightRecords.vue'
import ProfileModal from '../components/nutrition/ProfileModal.vue'
import WeightModal from '../components/nutrition/WeightModal.vue'
import GoalModal from '../components/nutrition/GoalModal.vue'
import CalorieProgressMeter from '../components/nutrition/CalorieProgressMeter.vue'

export default {
  name: 'NutritionDashboard',
  components: {
    BMRCalculator,
    GoalProgress,
    RecentWeightRecords,
    ProfileModal,
    WeightModal,
    GoalModal,
    CalorieProgressMeter
  },
  setup() {
    const dashboardData = ref({})
    const analyticsData = ref({})
    const selectedTimeRange = ref('30d')
    const showProfileModal = ref(false)
    const showWeightModal = ref(false)
    const showGoalModal = ref(false)
    const loading = ref(false)
    const error = ref(null)

    const hasProfile = computed(() => {
      return dashboardData.value?.profile?.age
    })

    const loadDashboard = async () => {
      try {
        loading.value = true
        error.value = null
        const data = await nutritionService.getDashboardSummary()
        dashboardData.value = data
      } catch (err) {
        console.error('Error loading dashboard:', err)
        error.value = err.response?.data?.message || 'Failed to load dashboard data'
      } finally {
        loading.value = false
      }
    }

    const loadAnalytics = async () => {
      try {
        error.value = null
        const data = await nutritionService.getWeightAnalytics(selectedTimeRange.value)
        analyticsData.value = data
      } catch (err) {
        console.error('Error loading analytics:', err)
        error.value = err.response?.data?.message || 'Failed to load analytics data'
      }
    }

    const handleBMRCalculated = (result) => {
      console.log('BMR/TDEE calculated:', result)
    }

    const handleProfileSaved = () => {
      showProfileModal.value = false
      loadDashboard()
      loadAnalytics()
    }

    const handleWeightSaved = () => {
      showWeightModal.value = false
      loadDashboard()
      loadAnalytics()
    }

    const handleGoalSaved = () => {
      showGoalModal.value = false
      loadDashboard()
      loadAnalytics()
    }

    onMounted(() => {
      loadDashboard()
      loadAnalytics()
    })

    return {
      dashboardData,
      analyticsData,
      selectedTimeRange,
      showProfileModal,
      showWeightModal,
      showGoalModal,
      hasProfile,
      loading,
      error,
      loadDashboard,
      loadAnalytics,
      handleBMRCalculated,
      handleProfileSaved,
      handleWeightSaved,
      handleGoalSaved
    }
  }
}
</script> 