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

        <!-- Meal Type Selector (Optional) -->
        <div class="mt-4">
          <div class="text-gray-300 mb-2">選擇餐別（可選）</div>
          <div class="flex gap-3">
            <label class="inline-flex items-center gap-2 text-gray-200 cursor-pointer">
              <input type="radio" name="mealType" class="form-radio" value="breakfast" v-model="mealType" />
              <span>早餐</span>
            </label>
            <label class="inline-flex items-center gap-2 text-gray-200 cursor-pointer">
              <input type="radio" name="mealType" class="form-radio" value="lunch" v-model="mealType" />
              <span>午餐</span>
            </label>
            <label class="inline-flex items-center gap-2 text-gray-200 cursor-pointer">
              <input type="radio" name="mealType" class="form-radio" value="dinner" v-model="mealType" />
              <span>晚餐</span>
            </label>
            <button
              type="button"
              class="ml-2 px-3 py-1 text-sm border border-gray-600 text-gray-300 rounded hover:bg-[#1e2021]"
              @click="mealType = null"
            >清除</button>
          </div>
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

        <div class="mt-6">
          <div class="text-gray-300 mb-2">也猜猜各營養素（克）</div>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <div>
              <label class="block text-sm text-gray-400 mb-1">碳水化合物</label>
              <input
                type="number"
                min="0"
                class="w-full px-3 py-2 rounded bg-[#1e2021] text-gray-200 border border-gray-700"
                v-model.number="guessCarbs"
                :disabled="loading"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-1">蛋白質</label>
              <input
                type="number"
                min="0"
                class="w-full px-3 py-2 rounded bg-[#1e2021] text-gray-200 border border-gray-700"
                v-model.number="guessProtein"
                :disabled="loading"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-1">脂肪</label>
              <input
                type="number"
                min="0"
                class="w-full px-3 py-2 rounded bg-[#1e2021] text-gray-200 border border-gray-700"
                v-model.number="guessFat"
                :disabled="loading"
              />
            </div>
            <div>
              <label class="block text-sm text-gray-400 mb-1">膳食纖維</label>
              <input
                type="number"
                min="0"
                class="w-full px-3 py-2 rounded bg-[#1e2021] text-gray-200 border border-gray-700"
                v-model.number="guessFiber"
                :disabled="loading"
              />
            </div>
          </div>
        </div>

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
        <div class="bg-[#2a2b2c] rounded-xl shadow-lg h-[800px] flex flex-col overflow-hidden">
          <div class="p-6 border-b border-gray-700">
            <h1 class="text-2xl font-semibold text-white">營養資訊</h1>
          </div>
          <div class="flex-1 p-6 flex flex-col overflow-hidden">
            <div v-if="result" class="h-full flex flex-col overflow-hidden">
              <div class="flex-1 flex justify-center items-center min-h-[400px]">
                <Doughnut v-if="chartData" :data="chartData" :options="chartOptions" />
              </div>
              <div class="space-y-3 mt-6 overflow-y-auto pr-2">
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
                <div v-if="result?.nutrition?.fiber !== undefined" class="flex justify-between items-center text-gray-200 text-lg">
                  <span>膳食纖維</span>
                  <span class="font-medium">{{ result.nutrition.fiber }} 克</span>
                </div>
                <div v-if="result?.nutrition?.sugar !== undefined" class="flex justify-between items-center text-gray-200 text-lg">
                  <span>糖</span>
                  <span class="font-medium">{{ result.nutrition.sugar }} 克</span>
                </div>
                <div v-if="result?.nutrition?.sodium_mg !== undefined" class="flex justify-between items-center text-gray-200 text-lg">
                  <span>鈉</span>
                  <span class="font-medium">{{ result.nutrition.sodium_mg }} 毫克</span>
                </div>
                <div v-if="result?.nutrition?.cholesterol_mg !== undefined" class="flex justify-between items-center text-gray-200 text-lg">
                  <span>膽固醇</span>
                  <span class="font-medium">{{ result.nutrition.cholesterol_mg }} 毫克</span>
                </div>
                <div v-if="result?.nutrition?.potassium_mg !== undefined" class="flex justify-between items-center text-gray-200 text-lg">
                  <span>鉀</span>
                  <span class="font-medium">{{ result.nutrition.potassium_mg }} 毫克</span>
                </div>

                <div v-if="result?.nutrition?.fat_breakdown" class="text-gray-200 mt-4">
                  <p class="mb-2 font-medium">脂肪細分</p>
                  <div class="space-y-2">
                    <div class="flex justify-between"><span class="text-gray-300">飽和脂肪</span><span class="font-medium">{{ result.nutrition.fat_breakdown.saturated_fat_g }} 克</span></div>
                    <div class="flex justify-between"><span class="text-gray-300">單元不飽和脂肪</span><span class="font-medium">{{ result.nutrition.fat_breakdown.monounsaturated_fat_g }} 克</span></div>
                    <div class="flex justify-between"><span class="text-gray-300">多元不飽和脂肪</span><span class="font-medium">{{ result.nutrition.fat_breakdown.polyunsaturated_fat_g }} 克</span></div>
                    <div class="flex justify-between"><span class="text-gray-300">反式脂肪</span><span class="font-medium">{{ result.nutrition.fat_breakdown.trans_fat_g }} 克</span></div>
                  </div>
                </div>

                <div class="text-gray-200 mt-4">
                  <p class="mb-2"><span class="font-medium">維生素：</span>{{ result.nutrition.vitamins }}</p>
                  <p><span class="font-medium">礦物質：</span>{{ result.nutrition.minerals }}</p>
                </div>

                <div v-if="result?.nutrition?.minerals_mg" class="text-gray-200 mt-4">
                  <p class="mb-2 font-medium">礦物質（毫克）</p>
                  <div class="grid grid-cols-2 gap-2 text-gray-300">
                    <div>鈣：{{ result.nutrition.minerals_mg.calcium }} mg</div>
                    <div>鐵：{{ result.nutrition.minerals_mg.iron }} mg</div>
                    <div>鎂：{{ result.nutrition.minerals_mg.magnesium }} mg</div>
                    <div>磷：{{ result.nutrition.minerals_mg.phosphorus }} mg</div>
                    <div>鋅：{{ result.nutrition.minerals_mg.zinc }} mg</div>
                  </div>
                </div>

                <div v-if="result?.nutrition?.vitamins_detail" class="text-gray-200 mt-4">
                  <p class="mb-2 font-medium">維生素詳情</p>
                  <div class="grid grid-cols-2 gap-2 text-gray-300">
                    <div>維生素 A：{{ result.nutrition.vitamins_detail.vitamin_a_ug_rae }} μg RAE</div>
                    <div>維生素 C：{{ result.nutrition.vitamins_detail.vitamin_c_mg }} mg</div>
                    <div>維生素 D：{{ result.nutrition.vitamins_detail.vitamin_d_ug }} μg</div>
                    <div>維生素 E：{{ result.nutrition.vitamins_detail.vitamin_e_mg }} mg</div>
                    <div>維生素 K：{{ result.nutrition.vitamins_detail.vitamin_k_ug }} μg</div>
                    <div>維生素 B1：{{ result.nutrition.vitamins_detail.thiamin_b1_mg }} mg</div>
                    <div>維生素 B2：{{ result.nutrition.vitamins_detail.riboflavin_b2_mg }} mg</div>
                    <div>維生素 B3：{{ result.nutrition.vitamins_detail.niacin_b3_mg }} mg</div>
                    <div>維生素 B6：{{ result.nutrition.vitamins_detail.vitamin_b6_mg }} mg</div>
                    <div>葉酸（B9，DFE）：{{ result.nutrition.vitamins_detail.folate_b9_ug_dfe }} μg</div>
                    <div>維生素 B12：{{ result.nutrition.vitamins_detail.vitamin_b12_ug }} μg</div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="h-full flex items-center justify-center text-gray-500">尚未有分析結果</div>
          </div>
        </div>

        <!-- Right: Results + Guess comparison -->
        <div class="flex flex-col h-[800px]">
          <!-- Editable fields for detections and calories -->
          <div class="bg-[#2a2b2c] rounded-xl shadow-lg p-6 mt-6">
            <h2 class="text-xl font-semibold text-white mb-4">編輯並儲存到歷史</h2>
            <div v-if="result" class="space-y-4">
              <!-- Editable detections list -->
              <div>
                <div class="flex items-center justify-between mb-2">
                  <h3 class="text-gray-200 font-medium">檢測項目</h3>
                  <button
                    class="px-2 py-1 text-sm bg-gray-700 text-white rounded hover:bg-gray-600"
                    @click="addEditableDetection"
                  >新增項目</button>
                </div>
                <div v-if="editableDetections.length === 0" class="text-gray-400 text-sm">目前無可編輯項目</div>
                <div v-for="(d, idx) in editableDetections" :key="idx" class="flex items-center gap-2 mb-2">
                  <input
                    class="flex-1 px-3 py-2 rounded bg-[#1e2021] text-gray-200 border border-gray-700"
                    v-model="d.item"
                    placeholder="項目名稱"
                  />
                  <span class="text-gray-400 text-sm" v-if="d.confidence !== undefined">{{ (d.confidence * 100).toFixed(0) }}%</span>
                  <button
                    class="px-2 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                    @click="removeEditableDetection(idx)"
                  >刪除</button>
                </div>
              </div>

              <!-- Editable total calories -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm text-gray-300 mb-1">總卡路里（大卡）</label>
                  <input
                    type="number"
                    class="w-full px-3 py-2 rounded bg-[#1e2021] text-gray-200 border border-gray-700"
                    v-model.number="editedTotalCalories"
                    min="0"
                  />
                </div>
                <div>
                  <label class="block text-sm text-gray-300 mb-1">餐別</label>
                  <div class="flex gap-3 text-gray-200">
                    <label class="inline-flex items-center gap-2 cursor-pointer">
                      <input type="radio" name="mealTypeEdit" value="breakfast" v-model="mealType" />
                      <span>早餐</span>
                    </label>
                    <label class="inline-flex items-center gap-2 cursor-pointer">
                      <input type="radio" name="mealTypeEdit" value="lunch" v-model="mealType" />
                      <span>午餐</span>
                    </label>
                    <label class="inline-flex items-center gap-2 cursor-pointer">
                      <input type="radio" name="mealTypeEdit" value="dinner" v-model="mealType" />
                      <span>晚餐</span>
                    </label>
                    <button type="button" class="px-2 py-1 text-sm border border-gray-600 rounded hover:bg-[#1e2021]" @click="mealType = null">清除</button>
                  </div>
                </div>
              </div>

              <div class="pt-2 text-right">
                <button
                  class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                  :disabled="loading || !file"
                  @click="saveHistory"
                >儲存到歷史</button>
              </div>
            </div>
            <div v-else class="text-gray-500">完成分析後可編輯並儲存</div>
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
            <div v-if="result" class="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-center text-gray-200">
              <div class="bg-[#1e2021] rounded-lg p-4">
                <div class="text-sm text-gray-400">碳水化合物</div>
                <div class="text-lg font-semibold mt-1">猜：{{ guessCarbs }} 克</div>
                <div class="text-lg font-semibold">結果：{{ actualCarbs }} 克</div>
                <div class="text-sm text-gray-400 mt-1">差距：{{ carbsDelta }} 克</div>
              </div>
              <div class="bg-[#1e2021] rounded-lg p-4">
                <div class="text-sm text-gray-400">蛋白質</div>
                <div class="text-lg font-semibold mt-1">猜：{{ guessProtein }} 克</div>
                <div class="text-lg font-semibold">結果：{{ actualProtein }} 克</div>
                <div class="text-sm text-gray-400 mt-1">差距：{{ proteinDelta }} 克</div>
              </div>
              <div class="bg-[#1e2021] rounded-lg p-4">
                <div class="text-sm text-gray-400">脂肪</div>
                <div class="text-lg font-semibold mt-1">猜：{{ guessFat }} 克</div>
                <div class="text-lg font-semibold">結果：{{ actualFat }} 克</div>
                <div class="text-sm text-gray-400 mt-1">差距：{{ fatDelta }} 克</div>
              </div>
              <div v-if="result?.nutrition?.fiber !== undefined" class="bg-[#1e2021] rounded-lg p-4">
                <div class="text-sm text-gray-400">膳食纖維</div>
                <div class="text-lg font-semibold mt-1">猜：{{ guessFiber }} 克</div>
                <div class="text-lg font-semibold">結果：{{ actualFiber }} 克</div>
                <div class="text-sm text-gray-400 mt-1">差距：{{ fiberDelta }} 克</div>
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
const guessCarbs = ref(0)
const guessProtein = ref(0)
const guessFat = ref(0)
const guessFiber = ref(0)
const loading = ref(false)
const result = ref(null)
const isDragging = ref(false)
const imageInput = ref(null)
const error = ref(null)
  const mealType = ref(null) // 'breakfast' | 'lunch' | 'dinner' | null

// Editable state derived from result
const editableDetections = ref([])
const editedTotalCalories = ref(0)

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

const actualCarbs = computed(() => (result.value?.nutrition?.carbs ?? 0))
const actualProtein = computed(() => (result.value?.nutrition?.protein ?? 0))
const actualFat = computed(() => (result.value?.nutrition?.fat ?? 0))
const actualFiber = computed(() => (result.value?.nutrition?.fiber ?? 0))

const carbsDelta = computed(() => Math.round(Math.abs((guessCarbs.value || 0) - (actualCarbs.value || 0))))
const proteinDelta = computed(() => Math.round(Math.abs((guessProtein.value || 0) - (actualProtein.value || 0))))
const fatDelta = computed(() => Math.round(Math.abs((guessFat.value || 0) - (actualFat.value || 0))))
const fiberDelta = computed(() => Math.round(Math.abs((guessFiber.value || 0) - (actualFiber.value || 0))))

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
  const th = 0.7
  return preds.filter(p => (p.confidence || 0) >= th)
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
      // Initialize editable fields after result ready
      initializeEditableFields()
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
  // Use edited values
  const detectionsPayload = (editableDetections.value || []).map(d => ({
    item: d.item,
    confidence: d.confidence,
    calories: result.value?.nutrition?.calories,
    carbs: result.value?.nutrition?.carbs,
    protein: result.value?.nutrition?.protein,
    fat: result.value?.nutrition?.fat
  }))
  formData.append('detections', JSON.stringify(detectionsPayload))
  formData.append('total_calories', editedTotalCalories.value || result.value.total_calories || 0)
    if (mealType.value) {
      formData.append('meal_type', mealType.value)
    }

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
  guessCarbs.value = 0
  guessProtein.value = 0
  guessFat.value = 0
  guessFiber.value = 0
  step.value = 1
}

function initializeEditableFields() {
  // Initialize detections from filtered predictions
  const preds = filteredPredictions.value || []
  editableDetections.value = preds.map(p => ({ item: p.name, confidence: p.confidence }))
  // Initialize calories from result
  editedTotalCalories.value = result.value?.total_calories || result.value?.nutrition?.calories || 0
}

function addEditableDetection() {
  editableDetections.value.push({ item: '', confidence: 0 })
}

function removeEditableDetection(index) {
  editableDetections.value.splice(index, 1)
}
</script>


