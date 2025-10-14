<template>
  <section class="max-w-6xl mx-auto px-6 py-12">
    <!-- Title -->
    <div class="text-center mb-12">
      <h1 class="text-4xl font-bold text-gray-800 mb-4">我的紀錄</h1>
      <p class="text-gray-600 text-lg">追蹤你的營養攝取歷程</p>
    </div>

    <!-- Filters and Controls -->
    <div class="bg-white rounded-2xl shadow-lg p-6 mb-8">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- Time Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            時間篩選
          </label>
          <select 
            v-model="filters.period" 
            @change="applyFilters"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">全部時間</option>
            <option value="today">今天</option>
            <option value="yesterday">昨天</option>
            <option value="this_week">本週</option>
            <option value="last_week">上週</option>
            <option value="this_month">本月</option>
            <option value="last_month">上月</option>
          </select>
        </div>

        <!-- Custom Date Range -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            開始日期
          </label>
          <input 
            type="date" 
            v-model="filters.dateFrom"
            @change="applyFilters"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            結束日期
          </label>
          <input 
            type="date" 
            v-model="filters.dateTo"
            @change="applyFilters"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <!-- Sort Options -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            排序方式
          </label>
          <select 
            v-model="sortOption" 
            @change="applyFilters"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="-created_at">最新時間</option>
            <option value="created_at">最舊時間</option>
            <option value="-total_calories">卡路里由高到低</option>
            <option value="total_calories">卡路里由低到高</option>
          </select>
        </div>
      </div>

      <!-- Calorie Range Filter -->
      <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            最低卡路里
          </label>
          <input 
            type="number" 
            v-model="filters.caloriesMin"
            @input="applyFilters"
            placeholder="例如: 100"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            最高卡路里
          </label>
          <input 
            type="number" 
            v-model="filters.caloriesMax"
            @input="applyFilters"
            placeholder="例如: 1000"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      <!-- Clear Filters Button -->
      <div class="mt-6 text-center">
        <button 
          @click="clearFilters"
          class="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition duration-200"
        >
          清除篩選
        </button>
      </div>
    </div>

    <!-- Stats Summary -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8" v-if="entries.length > 0">
      {{ logTemplateRender('stats-summary', `Showing stats summary, entries: ${entries.length}`) }}
      <div class="bg-gradient-to-r from-blue-500 to-blue-600 rounded-2xl p-6 text-white">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-blue-100 text-sm">總記錄數</p>
            <p class="text-3xl font-bold">{{ entries.length }}</p>
          </div>
          <div class="p-3 bg-blue-400 rounded-full">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
          </div>
        </div>
      </div>

      <div class="bg-gradient-to-r from-green-500 to-green-600 rounded-2xl p-6 text-white">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-green-100 text-sm">總卡路里</p>
            <p class="text-3xl font-bold">{{ totalCalories }}</p>
          </div>
          <div class="p-3 bg-green-400 rounded-full">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
          </div>
        </div>
      </div>

      <div class="bg-gradient-to-r from-purple-500 to-purple-600 rounded-2xl p-6 text-white">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-purple-100 text-sm">平均卡路里</p>
            <p class="text-3xl font-bold">{{ averageCalories }}</p>
          </div>
          <div class="p-3 bg-purple-400 rounded-full">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {{ logTemplateRender('loading', `Showing loading state, entries: ${entries.length}, error: ${error}`) }}
      <div
        v-for="i in 6"
        :key="i"
        class="bg-white rounded-2xl shadow-lg p-6 animate-pulse"
      >
        <div class="bg-gray-200 h-48 rounded-xl mb-4"></div>
        <div class="space-y-3">
          <div class="h-4 bg-gray-200 rounded w-3/4"></div>
          <div class="h-4 bg-gray-200 rounded w-1/2"></div>
          <div class="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="!entries.length && !error"
      class="text-center py-20"
    >
      {{ logTemplateRender('empty-state', `Showing empty state, entries: ${entries.length}, error: ${error}, loading: ${loading}`) }}
      <div class="max-w-md mx-auto">
        <div class="w-32 h-32 mx-auto mb-8 bg-gray-100 rounded-full flex items-center justify-center">
          <svg class="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
        </div>
        <h3 class="text-2xl font-semibold text-gray-800 mb-4">還沒有任何紀錄</h3>
        <p class="text-gray-600 mb-8">
          開始你的第一次食物掃描，建立你的營養追蹤記錄！
        </p>
        <RouterLink
          to="/classify"
          class="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-full hover:from-blue-600 hover:to-blue-700 transition duration-200 transform hover:scale-105 shadow-lg"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          立即開始掃描
        </RouterLink>
      </div>
    </div>

    <!-- History Cards Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {{ logTemplateRender('history-grid', `Showing history grid, entries: ${entries.length}, error: ${error}, loading: ${loading}`) }}
      <div
        v-for="entry in entries"
        :key="entry.id"
        class="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 overflow-hidden"
      >
        <!-- Image Section -->
        <div class="relative h-48 overflow-hidden">
          <img
            :src="entry.image"
            :alt="`食物掃描 - ${formatDate(entry.created_at)}`"
            class="w-full h-full object-cover transition-transform duration-300 hover:scale-110"
          />
          <div class="absolute top-4 right-4 bg-black bg-opacity-50 text-white px-3 py-1 rounded-full text-sm">
            {{ formatDateShort(entry.created_at) }}
          </div>
          <div class="absolute bottom-4 left-4 bg-green-500 text-white px-4 py-2 rounded-full font-bold shadow-lg">
            {{ entry.total_calories }} 卡
          </div>
        </div>

        <!-- Content Section -->
        <div class="p-6">
          <!-- Food Items -->
          <div class="mb-4">
            <h3 class="text-lg font-semibold text-gray-800 mb-2">檢測項目</h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="detection in entry.detections"
                :key="detection.item"
                class="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full"
              >
                {{ detection.item }}
                <span class="ml-1 text-blue-600">({{ detection.calories }}卡)</span>
              </span>
            </div>
          </div>

          <!-- Stats -->
          <div class="flex justify-between items-center pt-4 border-t border-gray-200">
            <div class="text-center">
              <p class="text-xs text-gray-500">項目數量</p>
              <p class="text-lg font-bold text-gray-800">{{ entry.detections.length }}</p>
            </div>
            <div class="text-center">
              <p class="text-xs text-gray-500">總卡路里</p>
              <p class="text-lg font-bold text-green-600">{{ entry.total_calories }}</p>
            </div>
            <div class="text-center">
              <p class="text-xs text-gray-500">掃描時間</p>
              <p class="text-sm font-medium text-gray-600">{{ formatTime(entry.created_at) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="text-center py-16">
      {{ logTemplateRender('error-state', `Showing error state, entries: ${entries.length}, error: ${error}, loading: ${loading}`) }}
      <div class="max-w-md mx-auto">
        <div class="w-24 h-24 mx-auto mb-6 bg-red-100 rounded-full flex items-center justify-center">
          <svg class="w-12 h-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-gray-800 mb-4">無法載入記錄</h3>
        <p class="text-gray-600 mb-6">
          請
          <RouterLink to="/accounts/login" class="text-blue-600 hover:text-blue-700 font-medium underline">
            登入
          </RouterLink>
          以查看你的營養記錄。
        </p>
        <button 
          @click="loadEntries"
          class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition duration-200"
        >
          重新載入
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { cookieStorage } from '../../utils/cookies'

// Normalize API base to always include /api/
const RAW_API_BASE = import.meta.env.VITE_API_BASE_URL || (typeof window !== 'undefined' ? `${window.location.origin}/api/` : 'http://localhost:8000/api/')
let API_BASE = RAW_API_BASE
if (!/\/api\/?$/.test(API_BASE)) {
  API_BASE = API_BASE.replace(/\/+$/, '') + '/api/'
}
if (!API_BASE.endsWith('/')) {
  API_BASE = API_BASE + '/'
}
// --- helper to do fetch with JWT header ---
async function authFetch(url, opts = {}) {
  const token = cookieStorage.getItem('access_token')
  console.log('authFetch: Making request to:', url)
  console.log('authFetch: Token present:', !!token)

  const headers = {
    'Content-Type': 'application/json',
    ...(opts.headers || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
  const res = await fetch(url, { ...opts, headers })

  console.log('authFetch: Response status:', res.status)
  console.log('authFetch: Response headers:', Object.fromEntries(res.headers.entries()))

  if (!res.ok) {
    // Try to get error details from response
    let errorMessage = `HTTP ${res.status}`
    try {
      const contentType = res.headers.get('content-type')
      console.log('authFetch: Error response content-type:', contentType)

      if (contentType && contentType.includes('application/json')) {
        const errorData = await res.json()
        console.log('authFetch: Error response JSON:', errorData)
        errorMessage = errorData.detail || errorData.message || errorMessage
      } else {
        // For non-JSON responses, try to get text
        const text = await res.text()
        console.log('authFetch: Error response text (first 200 chars):', text.substring(0, 200))
        if (text) {
          errorMessage = `HTTP ${res.status}: ${text.substring(0, 100)}...`
        }
      }
    } catch (e) {
      // If we can't parse the error response, just use the status
      console.warn('authFetch: Could not parse error response:', e)
    }
    console.error('authFetch: Throwing error:', errorMessage)
    throw new Error(errorMessage)
  }

  // Check if response is JSON before parsing
  const contentType = res.headers.get('content-type')
  console.log('authFetch: Success response content-type:', contentType)

  if (contentType && contentType.includes('application/json')) {
    const jsonData = await res.json()
    console.log('authFetch: Parsed JSON data:', jsonData)
    return jsonData
  } else {
    // For non-JSON responses, return the response object
    console.log('authFetch: Returning non-JSON response object')
    return res
  }
}

// Reactive data
const entries = ref([])
const loading = ref(false)
const error = ref(false)
const sortOption = ref('-created_at')

// Debug logging for template rendering
function logTemplateRender(condition, message) {
  console.log(`Template render [${condition}]: ${message}`)
}

// Filter state
const filters = ref({
  period: '',
  dateFrom: '',
  dateTo: '',
  caloriesMin: '',
  caloriesMax: ''
})

// Computed properties for stats
const totalCalories = computed(() => {
  return entries.value.reduce((sum, entry) => sum + entry.total_calories, 0)
})

const averageCalories = computed(() => {
  if (entries.value.length === 0) return 0
  return Math.round(totalCalories.value / entries.value.length)
})

// Date formatting functions
function formatDate(dateString) {
  return new Date(dateString).toLocaleString('zh-TW', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatDateShort(dateString) {
  return new Date(dateString).toLocaleDateString('zh-TW', {
    month: 'short',
    day: 'numeric'
  })
}

function formatTime(dateString) {
  return new Date(dateString).toLocaleTimeString('zh-TW', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Build query parameters for API call
function buildQueryParams() {
  console.log('buildQueryParams: Current filters:', filters.value)
  console.log('buildQueryParams: Current sort option:', sortOption.value)

  const params = new URLSearchParams()

  if (filters.value.period) {
    console.log('buildQueryParams: Adding period filter:', filters.value.period)
    params.append('period', filters.value.period)
  }

  if (filters.value.dateFrom) {
    console.log('buildQueryParams: Adding date_from filter:', filters.value.dateFrom)
    params.append('date_from', filters.value.dateFrom)
  }

  if (filters.value.dateTo) {
    console.log('buildQueryParams: Adding date_to filter:', filters.value.dateTo)
    params.append('date_to', filters.value.dateTo)
  }

  if (filters.value.caloriesMin) {
    console.log('buildQueryParams: Adding calories_min filter:', filters.value.caloriesMin)
    params.append('calories_min', filters.value.caloriesMin)
  }

  if (filters.value.caloriesMax) {
    console.log('buildQueryParams: Adding calories_max filter:', filters.value.caloriesMax)
    params.append('calories_max', filters.value.caloriesMax)
  }

  if (sortOption.value) {
    console.log('buildQueryParams: Adding ordering:', sortOption.value)
    params.append('ordering', sortOption.value)
  }

  const result = params.toString()
  console.log('buildQueryParams: Final query string:', result)
  return result
}

// Load entries from API
async function loadEntries() {
  console.log('loadEntries: Starting to load history entries')
  loading.value = true
  error.value = false
  try {
    const queryParams = buildQueryParams()
    const url = new URL('history/entries/', API_BASE)
    if (queryParams) url.search = queryParams
    console.log('loadEntries: API_BASE:', API_BASE)
    console.log('loadEntries: Final URL:', url.toString())
    console.log('loadEntries: Query params:', queryParams)

    const data = await authFetch(url)
    console.log('loadEntries: Received data:', data)
    console.log('loadEntries: Data type:', typeof data)
    console.log('loadEntries: Is array?', Array.isArray(data))
    console.log('loadEntries: Data length:', data ? data.length : 'N/A')

    if (!Array.isArray(data)) {
      console.error('loadEntries: Expected an array of entries but got:', data)
      entries.value = []
      error.value = true
      return
    }

    entries.value = data
    console.log('loadEntries: Set entries to:', entries.value)
  } catch (e) {
    console.error('loadEntries: fetch history failed:', e)
    console.error('loadEntries: Error stack:', e.stack)
    error.value = true
  } finally {
    loading.value = false
    console.log('loadEntries: Finished loading, loading state:', loading.value, 'error state:', error.value)
  }
}

// Apply filters
function applyFilters() {
  loadEntries()
}

// Clear all filters
function clearFilters() {
  filters.value = {
    period: '',
    dateFrom: '',
    dateTo: '',
    caloriesMin: '',
    caloriesMax: ''
  }
  sortOption.value = '-created_at'
  loadEntries()
}

// Watch for changes in entries
watch(entries, (newEntries, oldEntries) => {
  console.log('entries watcher: Entries changed')
  console.log('entries watcher: Old entries:', oldEntries)
  console.log('entries watcher: New entries:', newEntries)
  console.log('entries watcher: New entries length:', newEntries ? newEntries.length : 'N/A')
})

// Load data on component mount
onMounted(() => {
  console.log('HistoryList: Component mounted, calling loadEntries')
  console.log('HistoryList: Auth token present:', !!cookieStorage.getItem('access_token'))
  console.log('HistoryList: Refresh token present:', !!cookieStorage.getItem('refresh_token'))
  loadEntries()
})
</script>

<style scoped>
/* Custom scrollbar for webkit browsers */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* Smooth transitions for all interactive elements */
* {
  transition: all 0.2s ease-in-out;
}

/* Enhance focus states for accessibility */
input:focus, select:focus, button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Card hover effects */
.hover\:shadow-xl:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Gradient background animation */
@keyframes gradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.bg-gradient-to-r {
  background-size: 200% 200%;
  animation: gradient 3s ease infinite;
}
</style>



