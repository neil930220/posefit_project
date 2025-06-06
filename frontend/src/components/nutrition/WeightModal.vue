<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-1/2 lg:w-1/3 shadow-lg rounded-md bg-white">
      <!-- Modal Header -->
      <div class="flex items-center justify-between pb-4 border-b">
        <h3 class="text-lg font-medium text-gray-900">
          {{ isEditing ? '編輯體重記錄' : '新增體重記錄' }}
        </h3>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="mt-4">
        <form @submit.prevent="saveWeight" class="space-y-4">
          <!-- Weight -->
          <div>
            <label class="block text-sm font-medium text-gray-700">體重 (kg) *</label>
            <input 
              v-model.number="formData.weight" 
              type="number" 
              min="20" 
              max="500" 
              step="0.1"
              required
              class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="請輸入體重"
            >
          </div>

          <!-- Date -->
          <div>
            <label class="block text-sm font-medium text-gray-700">日期 *</label>
            <input 
              v-model="formData.date" 
              type="date" 
              required
              class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
          </div>

          <!-- Notes -->
          <div>
            <label class="block text-sm font-medium text-gray-700">備註</label>
            <textarea 
              v-model="formData.notes" 
              rows="3"
              class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="記錄當天的狀況或心得（選填）"
            ></textarea>
          </div>

          <!-- BMR/TDEE Preview -->
          <div v-if="calculatedValues" class="bg-gray-50 p-4 rounded-lg">
            <h4 class="text-sm font-medium text-gray-900 mb-2">預計計算值</h4>
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-gray-500">BMR:</span>
                <span class="font-medium ml-2">{{ calculatedValues.bmr }} kcal</span>
              </div>
              <div>
                <span class="text-gray-500">TDEE:</span>
                <span class="font-medium ml-2">{{ calculatedValues.tdee }} kcal</span>
              </div>
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
              {{ loading ? '儲存中...' : '儲存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import nutritionService from '../../services/nutritionService'

export default {
  name: 'WeightModal',
  props: {
    weightRecord: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const formData = ref({
      weight: '',
      date: new Date().toISOString().split('T')[0],
      notes: ''
    })

    const loading = ref(false)
    const error = ref('')
    const userProfile = ref(null)

    const isEditing = computed(() => {
      return props.weightRecord !== null
    })

    const calculatedValues = computed(() => {
      if (!userProfile.value || !formData.value.weight) return null
      
      const weight = parseFloat(formData.value.weight)
      if (isNaN(weight)) return null

      const bmr = userProfile.value.calculate_bmr ? 
        userProfile.value.calculate_bmr(weight) : 
        calculateBMR(weight)
      
      const tdee = bmr * (userProfile.value.activity_level || 1.2)

      return {
        bmr: Math.round(bmr),
        tdee: Math.round(tdee)
      }
    })

    const calculateBMR = (weight) => {
      if (!userProfile.value) return 0
      
      const { age, gender, height } = userProfile.value
      if (gender === 'M') {
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
      } else {
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
      }
    }

    const loadUserProfile = async () => {
      try {
        userProfile.value = await nutritionService.getUserProfile()
      } catch (error) {
        console.error('Error loading user profile:', error)
      }
    }

    const saveWeight = async () => {
      try {
        loading.value = true
        error.value = ''
        
        if (isEditing.value) {
          await nutritionService.updateWeightRecord(props.weightRecord.id, formData.value)
        } else {
          await nutritionService.addWeightRecord(formData.value)
        }
        
        emit('saved')
      } catch (err) {
        error.value = err.response?.data?.message || '儲存失敗，請重試'
        console.error('Error saving weight record:', err)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadUserProfile()
      
      if (isEditing.value) {
        formData.value = {
          weight: props.weightRecord.weight,
          date: props.weightRecord.date,
          notes: props.weightRecord.notes || ''
        }
      }
    })

    return {
      formData,
      loading,
      error,
      isEditing,
      calculatedValues,
      saveWeight
    }
  }
}
</script> 