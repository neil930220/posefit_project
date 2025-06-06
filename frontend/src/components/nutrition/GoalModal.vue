<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-1/2 lg:w-1/3 shadow-lg rounded-md bg-white">
      <!-- Modal Header -->
      <div class="flex items-center justify-between pb-4 border-b">
        <h3 class="text-lg font-medium text-gray-900">設定體重目標</h3>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="mt-4">
        <form @submit.prevent="saveGoal" class="space-y-4">
          <!-- Current Weight -->
          <div>
            <label class="block text-sm font-medium text-gray-700">目前體重 (kg) *</label>
            <input 
              v-model.number="formData.current_weight" 
              type="number" 
              min="20" 
              max="500" 
              step="0.1"
              required
              class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="請輸入目前體重"
            >
          </div>

          <!-- Start Weight -->
          <div>
            <label class="block text-sm font-medium text-gray-700">起始體重 (kg) *</label>
            <input 
              v-model.number="formData.start_weight" 
              type="number" 
              min="20" 
              max="500" 
              step="0.1"
              required
              class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="請輸入起始體重"
            >
          </div>

          <!-- Target Weight -->
          <div>
            <label class="block text-sm font-medium text-gray-700">目標體重 (kg) *</label>
            <input 
              v-model.number="formData.target_weight" 
              type="number" 
              min="20" 
              max="500" 
              step="0.1"
              required
              class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="請輸入目標體重"
            >
          </div>

          <!-- Start Date -->
          <div>
            <label class="block text-sm font-medium text-gray-700">開始日期 *</label>
            <input 
              v-model="formData.start_date" 
              type="date" 
              required
              class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
          </div>

          <!-- Target Date -->
          <div>
            <label class="block text-sm font-medium text-gray-700">目標日期 *</label>
            <input 
              v-model="formData.target_date" 
              type="date" 
              required
              :min="formData.start_date"
              class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
          </div>

          <!-- Goal Summary -->
          <div v-if="goalSummary" class="bg-blue-50 p-4 rounded-lg">
            <h4 class="text-sm font-medium text-blue-900 mb-2">目標摘要</h4>
            <div class="text-sm text-blue-800 space-y-1">
              <p><strong>目標類型:</strong> {{ goalSummary.type }}</p>
              <p><strong>需要變化:</strong> {{ goalSummary.weightChange }}kg</p>
              <p><strong>時間期限:</strong> {{ goalSummary.duration }}天</p>
              <p><strong>每週目標:</strong> {{ goalSummary.weeklyTarget }}kg/週</p>
              <p v-if="goalSummary.isRealistic" class="text-green-700">✅ 這是一個合理的目標</p>
              <p v-else class="text-red-700">⚠️ 建議調整目標，每週變化不超過0.5-1kg較為健康</p>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="flex">
              <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800">儲存失敗</h3>
                <p class="mt-1 text-sm text-red-700">{{ error }}</p>
              </div>
            </div>
          </div>

          <!-- Modal Footer -->
          <div class="flex justify-end space-x-3 pt-4 border-t">
            <button 
              type="button" 
              @click="$emit('close')"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
            >
              取消
            </button>
            <button 
              type="submit"
              :disabled="loading"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400"
            >
              {{ loading ? '儲存中...' : '設定目標' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import nutritionService from '../../services/nutritionService'

export default {
  name: 'GoalModal',
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const formData = ref({
      current_weight: '',
      start_weight: '',
      target_weight: '',
      start_date: new Date().toISOString().split('T')[0],
      target_date: ''
    })

    const loading = ref(false)
    const error = ref('')

    const goalSummary = computed(() => {
      const { current_weight, start_weight, target_weight, start_date, target_date } = formData.value
      
      if (!current_weight || !start_weight || !target_weight || !start_date || !target_date) {
        return null
      }

      const weightChange = Math.abs(target_weight - start_weight)
      const startDate = new Date(start_date)
      const endDate = new Date(target_date)
      const duration = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24))
      const weeklyTarget = duration > 0 ? (weightChange / (duration / 7)) : 0

      const type = target_weight > start_weight ? '增重' : target_weight < start_weight ? '減重' : '維持體重'
      const isRealistic = weeklyTarget <= 1 && weeklyTarget >= 0.1

      return {
        type,
        weightChange: weightChange.toFixed(1),
        duration,
        weeklyTarget: weeklyTarget.toFixed(2),
        isRealistic
      }
    })

    const loadCurrentWeight = async () => {
      try {
        const records = await nutritionService.getWeightRecords()
        if (records.length > 0) {
          const latestWeight = records[0].weight
          formData.value.current_weight = latestWeight
          formData.value.start_weight = latestWeight
        }
      } catch (error) {
        console.error('Error loading current weight:', error)
      }
    }

    const saveGoal = async () => {
      try {
        loading.value = true
        error.value = ''
        
        await nutritionService.createGoal(formData.value)
        emit('saved')
      } catch (err) {
        error.value = err.response?.data?.message || '儲存失敗，請重試'
        console.error('Error saving goal:', err)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadCurrentWeight()
      
      // Set default target date to 3 months from now
      const targetDate = new Date()
      targetDate.setMonth(targetDate.getMonth() + 3)
      formData.value.target_date = targetDate.toISOString().split('T')[0]
    })

    return {
      formData,
      loading,
      error,
      goalSummary,
      saveGoal
    }
  }
}
</script> 