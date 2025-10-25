<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-5xl mx-auto">
      <!-- Progress Header -->
      <div class="flex items-center justify-between mb-6">
        <div class="flex-1 h-2 bg-gray-200 rounded">
          <div
            class="h-2 bg-blue-600 rounded transition-all"
            :style="{ width: progressWidth }"
          />
        </div>
        <div class="ml-4 text-sm text-gray-600">
          第 {{ step }} 步，共 3 步
        </div>
      </div>

      <!-- Steps -->
      <div v-if="step === 1" class="bg-[#2a2b2c] rounded-xl shadow-lg p-6">
        <h2 class="text-xl font-semibold text-white mb-4">上傳圖片</h2>
        <div
          class="relative border-2 border-dashed border-gray-500 rounded-lg h-80 flex items-center justify-center cursor-pointer transition hover:border-gray-400 bg-[#1e2021] text-center"
          :class="{ 'bg-[#2d2e2f]': isDragging }"
          @dragover.prevent="onDragOver"
          @dragleave.prevent="onDragLeave"
          @drop.prevent="onDrop"
          @click="triggerFileSelect"
        >
          <template v-if="previewUrl">
            <img :src="previewUrl" alt="Selected preview" class="max-h-72 object-contain rounded-md" />
          </template>
          <template v-else>
            <p class="text-gray-400">拖曳圖片進來，或點此上傳</p>
          </template>
          <input ref="imageInput" type="file" accept="image/*" class="sr-only" @change="onFilePicked" />
        </div>

        <div class="mt-6 flex justify-end space-x-3">
          <button
            class="px-6 py-2 border border-gray-600 text-gray-200 rounded-lg hover:bg-[#1e2021] transition"
            @click="reset"
            :disabled="loading"
          >
            重置
          </button>
          <button
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            :disabled="!file || loading"
            @click="goNext"
          >
            下一步
          </button>
        </div>
      </div>

      <div v-else-if="step === 2" class="bg-[#2a2b2c] rounded-xl shadow-lg p-6">
        <h2 class="text-xl font-semibold text-white mb-4">猜猜熱量</h2>
        <p class="text-gray-300 mb-4">在分析過程中，先猜測這道餐點的總熱量（大卡）。</p>

        <GuessGame v-model="guessKcal" :disabled="loading" />

        <div class="mt-6 flex justify-between">
          <button
            class="px-6 py-2 border border-gray-600 text-gray-200 rounded-lg hover:bg-[#1e2021] transition"
            @click="goBack"
            :disabled="loading"
          >
            上一步
          </button>
          <button
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            @click="onSubmit"
            :disabled="loading || !file"
          >
            {{ loading ? '分析中…' : '提交猜測並分析' }}
          </button>
        </div>

        <div v-if="loading" class="mt-6 text-center text-gray-300">
          圖片上傳與分析中，請稍候…
        </div>
        <div v-if="error" class="mt-6 bg-red-100 text-red-800 p-4 rounded-xl text-center">
          無法辨識，請重新拍攝
        </div>
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Left: Nutrition Info -->
        <div class="bg-[#2a2b2c] rounded-xl shadow-lg h-[800px] flex flex-col">
          <div class="p-6 border-b border-gray-700">
            <h1 class="text-2xl font-semibold text-white">營養資訊</h1>
          </div>
          <div class="flex-1 p-6 flex flex-col">
            <div v-if="result" class="h-full flex flex-col">
              <div class="flex-1 flex justify-center items-center min-h-[400px]">
                <Doughnut v-if="chartData" :data="chartData" :options="chartOptions" />
              </div>
              <div class="space-y-3 mt-6">
                <div class="flex justify-between items-center text-gray-200 text-lg">
                  <span>熱量</span>
                  <span class="font-medium">{{ finalCalories }} 大卡</span>
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
                  <p class="mb-2"><span class="font-medium">維生素：</span>{{ result.nutrition.vitamins }}</p>
                  <p><span class="font-medium">礦物質：</span>{{ result.nutrition.minerals }}</p>
                </div>
              </div>
            </div>
            <div v-else class="h-full flex items-center justify-center text-gray-500">尚未有分析結果</div>
          </div>
        </div>

        <!-- Right: Results + Guess comparison -->
        <div class="flex flex-col h-[800px]">
          <div class="bg-[#2a2b2c] rounded-xl shadow-lg p-6 flex-1">
            <h2 class="text-2xl font-semibold text-white mb-4">預測結果</h2>
            <div v-if="result">
              <div class="mb-4">
                <label class="block text-sm text-gray-300 mb-2">顯示門檻（信心百分比）: <span class="font-semibold">{{ confidenceThreshold }}%</span></label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="1"
                  v-model.number="confidenceThreshold"
                  class="w-full"
                />
                <div v-if="hiddenCount > 0" class="mt-1 text-xs text-gray-400">已隱藏 {{ hiddenCount }} 項低於門檻的分類</div>
              </div>
              <h3 class="text-lg font-semibold text-gray-200 mb-3">檢測到的食物</h3>
              <div class="space-y-2 mb-4">
                <div v-if="filteredPredictions.length === 0" class="text-gray-400">目前門檻下沒有項目</div>
                <div v-for="pred in filteredPredictions" :key="pred.name" class="flex justify-between text-gray-200 text-lg">
                  <span>{{ pred.name }}</span>
                  <span class="font-medium">{{ (pred.confidence * 100).toFixed(1) }}%</span>
                </div>
              </div>
              <div class="pt-4 border-t border-gray-600">
                <div class="flex justify-between text-gray-200 text-lg">
                  <span>食物面積比</span>
                  <span class="font-medium">{{ result.ratio }}</span>
                </div>
              </div>
            </div>
            <div v-else class="text-gray-500">尚未有預測</div>
          </div>

          <div class="bg-[#2a2b2c] rounded-xl shadow-lg p-6 mt-6">
            <h2 class="text-xl font-semibold text-white mb-4">你的猜測 vs 結果</h2>
            <div v-if="result" class="grid grid-cols-3 gap-4 text-center text-gray-200">
              <div class="bg-[#1e2021] rounded-lg p-4">
                <div class="text-sm text-gray-400">你的猜測</div>
                <div class="text-2xl font-bold mt-1">{{ guessKcal }} kcal</div>
              </div>
              <div class="bg-[#1e2021] rounded-lg p-4">
                <div class="text-sm text-gray-400">實際結果</div>
                <div class="text-2xl font-bold mt-1">{{ finalCalories }} kcal</div>
              </div>
              <div class="bg-[#1e2021] rounded-lg p-4">
                <div class="text-sm text-gray-400">差距</div>
                <div class="text-2xl font-bold mt-1">{{ calorieDelta }} kcal</div>
              </div>
            </div>
            <div v-else class="text-gray-500">完成分析後會顯示比較結果</div>
          </div>

          <div class="mt-6 flex justify-between">
            <button class="px-6 py-2 border border-gray-600 text-gray-200 rounded-lg hover:bg-[#1e2021] transition" @click="restart">
              重新開始
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  
</template>

<script setup>
import { ref, computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import GuessGame from '../components/classify/GuessGame.vue'
import api from '../services/api'
import { cookieStorage } from '../utils/cookies'

ChartJS.register(ArcElement, Tooltip, Legend)

const step = ref(1)
const file = ref(null)
const previewUrl = ref(null)
const guessKcal = ref(400)
const loading = ref(false)
const result = ref(null)
const isDragging = ref(false)
const imageInput = ref(null)
const error = ref(null)
const confidenceThreshold = ref(50)

const progressWidth = computed(() => {
  if (step.value === 1) return '33%'
  if (step.value === 2) return '66%'
  return '100%'
})

const finalCalories = computed(() => {
  if (!result.value) return 0
  return result.value.total_calories || result.value.nutrition?.calories || 0
})

const calorieDelta = computed(() => {
  const delta = Math.abs((finalCalories.value || 0) - (guessKcal.value || 0))
  return Math.round(delta)
})

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
      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
      hoverBackgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
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
        font: { size: 14 }
      }
    }
  },
  cutout: '70%'
}

const filteredPredictions = computed(() => {
  const preds = result.value?.predictions || []
  const th = (confidenceThreshold.value || 0) / 100
  return preds.filter(p => (p.confidence || 0) >= th)
})

const hiddenCount = computed(() => {
  const total = result.value?.predictions?.length || 0
  return Math.max(0, total - filteredPredictions.value.length)
})

function onDragOver() { isDragging.value = true }
function onDragLeave() { isDragging.value = false }
function onDrop(e) {
  isDragging.value = false
  const dropped = e.dataTransfer.files[0]
  if (dropped && dropped.type.startsWith('image/')) { pickFile(dropped) }
}
function triggerFileSelect() { imageInput.value.click() }
function onFilePicked(e) {
  const picked = e.target.files[0]
  if (picked && picked.type.startsWith('image/')) { pickFile(picked) }
}
function pickFile(chosenFile) {
  file.value = chosenFile
  previewUrl.value = URL.createObjectURL(chosenFile)
  result.value = null
  error.value = null
}

function goNext() { if (file.value) step.value = 2 }
function goBack() { step.value = Math.max(1, step.value - 1) }

async function onSubmit() {
  if (!file.value) return
  loading.value = true
  result.value = null
  error.value = null

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
    if (data.error) {
      error.value = data
    } else {
      result.value = data
      step.value = 3
      await saveHistory()
    }
  } catch (err) {
    console.error('Upload error:', err)
    error.value = { message: '分析失敗，請稍後再試' }
  } finally {
    loading.value = false
  }
}

async function saveHistory() {
  if (!result.value) return
  const token = cookieStorage.getItem('access_token')
  if (!token) return

  const formData = new FormData()
  formData.append('image', file.value)

  const detections = (result.value.predictions || []).map(p => ({
    item: p.name,
    confidence: p.confidence,
    calories: result.value.nutrition?.calories,
    carbs: result.value.nutrition?.carbs,
    protein: result.value.nutrition?.protein,
    fat: result.value.nutrition?.fat
  }))

  formData.append('detections', JSON.stringify(detections))
  formData.append('total_calories', result.value.total_calories || 0)

  try {
    await api.post('/api/history/entries/', formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    })
  } catch (err) {
    console.error('History save error:', err.response?.data || err.message)
  }
}

function reset() {
  file.value = null
  previewUrl.value = null
  result.value = null
  loading.value = false
  error.value = null
  if (imageInput.value) imageInput.value.value = ''
}

function restart() {
  reset()
  guessKcal.value = 400
  step.value = 1
}
</script>


