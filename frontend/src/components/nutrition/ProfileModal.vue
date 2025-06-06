<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
      <!-- Modal Header -->
      <div class="flex items-center justify-between pb-4 border-b">
        <h3 class="text-lg font-medium text-gray-900">個人資料設定</h3>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="mt-4">
        <form @submit.prevent="saveProfile" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Age -->
            <div>
              <label class="block text-sm font-medium text-gray-700">年齡 *</label>
              <input 
                v-model.number="formData.age" 
                type="number" 
                min="1" 
                max="120"
                required
                class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="請輸入年齡"
              >
            </div>

            <!-- Gender -->
            <div>
              <label class="block text-sm font-medium text-gray-700">性別 *</label>
              <select 
                v-model="formData.gender" 
                required
                class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">請選擇性別</option>
                <option value="M">男性</option>
                <option value="F">女性</option>
              </select>
            </div>

            <!-- Height -->
            <div>
              <label class="block text-sm font-medium text-gray-700">身高 (cm) *</label>
              <input 
                v-model.number="formData.height" 
                type="number" 
                min="50" 
                max="300" 
                step="0.1"
                required
                class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="請輸入身高"
              >
            </div>

            <!-- Activity Level -->
            <div>
              <label class="block text-sm font-medium text-gray-700">活動量 *</label>
              <select 
                v-model.number="formData.activity_level" 
                required
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

            <!-- Goal -->
            <div>
              <label class="block text-sm font-medium text-gray-700">健康目標</label>
              <select 
                v-model="formData.goal" 
                class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="maintain">維持體重</option>
                <option value="lose">減重</option>
                <option value="gain">增重</option>
              </select>
            </div>

            <!-- Target Weight -->
            <div>
              <label class="block text-sm font-medium text-gray-700">目標體重 (kg)</label>
              <input 
                v-model.number="formData.target_weight" 
                type="number" 
                min="20" 
                max="500" 
                step="0.1"
                class="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="請輸入目標體重"
              >
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
import { ref, onMounted } from 'vue'
import nutritionService from '../../services/nutritionService'

export default {
  name: 'ProfileModal',
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const formData = ref({
      age: '',
      gender: '',
      height: '',
      activity_level: '',
      goal: 'maintain',
      target_weight: ''
    })

    const loading = ref(false)
    const error = ref('')

    const loadProfile = async () => {
      try {
        const profile = await nutritionService.getUserProfile()
        if (profile) {
          formData.value = {
            age: profile.age || '',
            gender: profile.gender || '',
            height: profile.height || '',
            activity_level: profile.activity_level || '',
            goal: profile.goal || 'maintain',
            target_weight: profile.target_weight || ''
          }
        }
      } catch (error) {
        console.error('Error loading profile:', error)
      }
    }

    const saveProfile = async () => {
      try {
        loading.value = true
        error.value = ''
        
        await nutritionService.createOrUpdateProfile(formData.value)
        emit('saved')
      } catch (err) {
        error.value = err.response?.data?.message || '儲存失敗，請重試'
        console.error('Error saving profile:', err)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadProfile()
    })

    return {
      formData,
      loading,
      error,
      saveProfile
    }
  }
}
</script> 