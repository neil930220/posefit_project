<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Left Section: Nutrition Information -->
      <div class="bg-[#2a2b2c] rounded-xl shadow-lg h-[800px] flex flex-col">
        <div class="p-6 border-b border-gray-700">
          <h1 class="text-2xl font-semibold text-white">營養資訊</h1>
        </div>
        
        <div class="flex-1 p-6 flex flex-col">
          <div v-if="result" class="h-full flex flex-col">
            <!-- Pie Chart -->
            <div class="flex-1 flex justify-center items-center min-h-[400px]">
              <Doughnut
                v-if="chartData"
                :data="chartData"
                :options="chartOptions"
              />
            </div>
            
            <!-- Detailed Nutrition Info -->
            <div class="space-y-3 mt-6">
              <div class="flex justify-between items-center text-gray-200 text-lg">
                <span>熱量</span>
                <span class="font-medium">{{ result.nutrition.calories }} 大卡</span>
              </div>
              <div class="flex justify-between items-center text-gray-200 text-lg">
                <span>碳水化合物</span>
                <span class="font-medium">{{ result.nutrition.carbs }} 克</span>
              </div>
              <div class="flex justify-between items-center text-gray-200 text-lg">
                <span>蛋白質</span>
                <span class="font-medium">{{ result.nutrition.protein }} 克</span>
              </div>
              <div class="flex justify-between items-center text-gray-200 text-lg">
                <span>脂肪</span>
                <span class="font-medium">{{ result.nutrition.fat }} 克</span>
              </div>
              <div class="text-gray-200 mt-4">
                <p class="mb-2">
                  <span class="font-medium">維生素：</span>
                  {{ result.nutrition.vitamins }}
                </p>
                <p>
                  <span class="font-medium">礦物質：</span>
                  {{ result.nutrition.minerals }}
                </p>
              </div>
            </div>
          </div>
          
          <!-- Placeholder when no result -->
          <div v-else class="h-full flex items-center justify-center text-gray-500">
            請上傳圖片以查看營養資訊
          </div>
        </div>
      </div>

      <!-- Right Section: Upload and Results -->
      <div class="flex flex-col h-[800px]">
        <!-- Upload Card -->
        <div class="bg-[#2a2b2c] rounded-xl shadow-lg flex-1">
  <!-- Drop Zone -->
          <div class="h-full flex flex-col">
  <div
              class="relative border-2 border-dashed border-gray-500 rounded-lg m-6 flex-1 cursor-pointer transition hover:border-gray-400 text-center bg-[#1e2021] flex flex-col justify-center"
              :class="{ 'bg-[#2d2e2f]': isDragging }"
    @dragover.prevent="onDragOver"
    @dragleave.prevent="onDragLeave"
    @drop.prevent="onDrop"
    @click="triggerFileSelect"
  >
    <!-- Image preview OR placeholder -->
    <template v-if="previewUrl">
      <img
        :src="previewUrl"
        alt="Selected preview"
                  class="mx-auto max-h-[400px] object-contain rounded-md"
      />
    </template>
    <template v-else>
                <p class="text-gray-400">拖曳圖片進來，或點此上傳</p>
    </template>

    <!-- Hidden File Input -->
    <input
      ref="imageInput"
      type="file"
      accept="image/*"
      class="sr-only"
      @change="onFilePicked"
    />
  </div>

            <!-- Action Buttons -->
            <div class="flex justify-center space-x-4 p-6">
        <button
                v-if="file"
          @click="onSubmit"
          :disabled="loading"
                class="px-8 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 text-lg"
        >
          {{ loading ? '上傳中…' : '上傳並分析' }}
        </button>
        <button
                v-if="file"
          @click="reset"
          :disabled="loading"
                class="px-8 py-2 border border-gray-600 text-gray-200 rounded-lg hover:bg-[#1e2021] transition text-lg"
        >
          再試一次
        </button>
            </div>
      </div>
    </div>

        <!-- Results Card -->
        <div v-if="result" class="bg-[#2a2b2c] rounded-xl shadow-lg mt-6">
          <div class="p-6 border-b border-gray-700">
            <h2 class="text-2xl font-semibold text-white">預測結果</h2>
          </div>
          <div class="p-6">
            <ul class="space-y-4 text-gray-200">
              <li class="flex justify-between text-lg">
                <span>類別</span>
                <span class="font-medium">{{ result.prediction }}</span>
        </li>
              <li class="flex justify-between text-lg">
                <span>信心分數</span>
                <span class="font-medium">{{ result.confidence }}</span>
        </li>
              <li class="flex justify-between text-lg">
                <span>食物面積比</span>
                <span class="font-medium">{{ result.ratio }}</span>
        </li>
      </ul>
          </div>
    </div>

        <!-- Error Message -->
    <div
      v-if="error"
          class="bg-red-100 text-red-800 p-4 rounded-xl text-center mt-6"
    >
      <h3 class="font-medium">無法辨識，請重新拍攝</h3>
        </div>
      </div>
    </div>
  </div>
</template>
  
<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import api from '../services/api'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { cookieStorage } from '../utils/cookies'

ChartJS.register(ArcElement, Tooltip, Legend)

const file = ref(null)
const previewUrl = ref(null)
const loading = ref(false)
const result = ref(null)
const isDragging = ref(false)
const imageInput = ref(null)
const error = ref(null)

const chartData = computed(() => {
  if (!result.value?.nutrition) return null
  
  return {
    labels: ['碳水化合物', '蛋白質', '脂肪'],
    datasets: [{
      data: [
        result.value.nutrition.carbs,
        result.value.nutrition.protein,
        result.value.nutrition.fat
      ],
      backgroundColor: [
        '#FF6384',
        '#36A2EB',
        '#FFCE56'
      ],
      hoverBackgroundColor: [
        '#FF6384',
        '#36A2EB',
        '#FFCE56'
      ],
      borderWidth: 0
    }]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        color: '#fff',
        padding: 20,
        font: {
          size: 14
        }
      }
    }
  },
  cutout: '70%'
}

function onDragOver() {
  isDragging.value = true
}
function onDragLeave() {
  isDragging.value = false
}
function onDrop(e) {
  isDragging.value = false
  const dropped = e.dataTransfer.files[0]
  if (dropped && dropped.type.startsWith('image/')) {
    pickFile(dropped)
  }
}
function triggerFileSelect() {
  imageInput.value.click()
}
function onFilePicked(e) {
  const picked = e.target.files[0]
  if (picked && picked.type.startsWith('image/')) {
    pickFile(picked)
  }
}
function pickFile(chosenFile) {
  file.value       = chosenFile
  previewUrl.value = URL.createObjectURL(chosenFile)
  result.value     = null
}

async function onSubmit() {
  if (!file.value) return
  loading.value = true
  result.value  = null
  error.value      = null

  try {
    const token = cookieStorage.getItem('access_token')
    const form = new FormData()
    form.append('image', file.value)
    const { data } = await api.post('api/upload/', form, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      },
      withCredentials: true
    })
    console.log(data)
    if (data.error) {
      error.value  = data
    }else{
      result.value  = data
      await saveHistory()
    }
  } catch (err) {
    console.error('Upload error:', err)
    alert('分析失敗，請稍後再試')
  } finally {
    loading.value = false
  }
}

async function saveHistory() {
  if (!result.value) return
  const token = cookieStorage.getItem('access_token')
  if (!token) return console.warn('⚠️ No token; cannot save history')

  const formData = new FormData()
  formData.append('image', file.value)
  formData.append('detections', JSON.stringify([{
    item: result.value.prediction,
    calories: result.value.nutrition.calories,
    carbs: result.value.nutrition.carbs,
    protein: result.value.nutrition.protein,
    fat: result.value.nutrition.fat
  }]))
  formData.append('total_calories', result.value.nutrition.calories)

  try {
    await api.post('/api/history/entries/', formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    })
  } catch (err) {
    console.error('History save error:', err.response?.data || err.message)
    // Don't show error to user as this is a non-critical operation
  }
}

function reset() {
  file.value       = null
  previewUrl.value = null
  result.value     = null
  loading.value    = false
  error.value      = null
  imageInput.value.value = ''
}
</script>
  