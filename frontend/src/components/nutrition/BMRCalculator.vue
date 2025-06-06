<template>
  <div class="space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Personal Information -->
      <div class="space-y-4">
        <h3 class="text-lg font-medium text-gray-900">個人資料</h3>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">年齡</label>
          <input 
            v-model.number="formData.age" 
            type="number" 
            min="1" 
            max="120"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="請輸入您的年齡"
          >
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">性別</label>
          <select 
            v-model="formData.gender" 
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">請選擇性別</option>
            <option value="M">男性</option>
            <option value="F">女性</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">身高 (cm)</label>
          <input 
            v-model.number="formData.height" 
            type="number" 
            min="50" 
            max="300" 
            step="0.1"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="請輸入身高"
          >
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">體重 (kg)</label>
          <input 
            v-model.number="formData.weight" 
            type="number" 
            min="20" 
            max="500" 
            step="0.1"
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="請輸入體重"
          >
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">活動量</label>
          <select 
            v-model.number="formData.activity_level" 
            class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">請選擇活動量</option>
            <option :value="1.2">久坐不動（幾乎不運動）</option>
            <option :value="1.375">輕度活動（每週運動1-3天）</option>
            <option :value="1.55">中度活動（每週運動3-5天）</option>
            <option :value="1.725">高度活動（每週運動6-7天）</option>
            <option :value="1.9">極高活動（重體力工作+運動）</option>
          </select>
        </div>
      </div>

      <!-- Results -->
      <div class="space-y-4">
        <h3 class="text-lg font-medium text-gray-900">計算結果</h3>
        
        <div v-if="loading" class="flex items-center justify-center h-32">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>

        <div v-else-if="results" class="space-y-4">
          <div class="bg-blue-50 p-4 rounded-lg">
            <h4 class="font-medium text-blue-900">基礎代謝率 (BMR)</h4>
            <p class="text-2xl font-bold text-blue-600">{{ results.bmr }} kcal/天</p>
            <p class="text-sm text-blue-700 mt-1">身體維持基本生理功能所需的最低熱量</p>
          </div>

          <div class="bg-green-50 p-4 rounded-lg">
            <h4 class="font-medium text-green-900">每日消耗總熱量 (TDEE)</h4>
            <p class="text-2xl font-bold text-green-600">{{ results.tdee }} kcal/天</p>
            <p class="text-sm text-green-700 mt-1">包含日常活動的總消耗熱量</p>
          </div>

          <div class="bg-gray-50 p-4 rounded-lg">
            <h4 class="font-medium text-gray-900">體重管理建議</h4>
            <div class="text-sm text-gray-700 mt-2 space-y-1">
              <p><strong>維持體重：</strong> {{ results.tdee }} kcal/天</p>
              <p><strong>減重（每週0.5kg）：</strong> {{ Math.round(results.tdee - 385) }} kcal/天</p>
              <p><strong>增重（每週0.5kg）：</strong> {{ Math.round(results.tdee + 385) }} kcal/天</p>
            </div>
          </div>
        </div>

        <div v-else class="text-center text-gray-500 py-8">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          <p class="mt-2">填寫上方資料以計算BMR和TDEE</p>
        </div>
      </div>
    </div>

    <!-- Calculate Button -->
    <div class="flex justify-center">
      <button 
        @click="calculate"
        :disabled="!isFormValid || loading"
        class="bg-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {{ loading ? '計算中...' : '計算 BMR / TDEE' }}
      </button>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex">
        <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">計算錯誤</h3>
          <p class="mt-1 text-sm text-red-700">{{ error }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, emit } from 'vue'
import nutritionService from '../../services/nutritionService'

export default {
  name: 'BMRCalculator',
  emits: ['calculated'],
  setup(props, { emit }) {
    const formData = ref({
      age: '',
      gender: '',
      height: '',
      weight: '',
      activity_level: ''
    })

    const results = ref(null)
    const loading = ref(false)
    const error = ref('')

    const isFormValid = computed(() => {
      return formData.value.age && 
             formData.value.gender && 
             formData.value.height && 
             formData.value.weight && 
             formData.value.activity_level
    })

    const calculate = async () => {
      if (!isFormValid.value) return

      try {
        loading.value = true
        error.value = ''
        
        const result = await nutritionService.calculateBMRTDEE(formData.value)
        results.value = result
        
        emit('calculated', result)
      } catch (err) {
        error.value = err.response?.data?.message || '計算時發生錯誤，請重試'
        console.error('BMR calculation error:', err)
      } finally {
        loading.value = false
      }
    }

    return {
      formData,
      results,
      loading,
      error,
      isFormValid,
      calculate
    }
  }
}
</script> 