<template>
  <div class="max-w-md mx-auto p-6 space-y-6">
  <!-- Drop Zone -->
  <div
    class="relative border-2 border-dashed border-gray-300 rounded-lg p-6 cursor-pointer transition hover:bg-gray-50 text-center"
    :class="{ 'bg-gray-100': isDragging }"
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
        class="mx-auto max-h-64 object-contain rounded-md"
      />
    </template>
    <template v-else>
      <p class="text-gray-500">拖曳圖片進來，或點此上傳</p>
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

    <!-- Preview & Actions -->
    <div v-if="file" class="flex flex-col items-center space-y-4">
      <div class="flex space-x-4">
        <button
          @click="onSubmit"
          :disabled="loading"
          class="px-6 py-2 bg-gray-800 text-white rounded-lg hover:bg-black transition disabled:opacity-50"
        >
          {{ loading ? '上傳中…' : '上傳並分析' }}
        </button>
        <button
          @click="reset"
          :disabled="loading"
          class="px-6 py-2 border border-gray-400 text-gray-800 rounded-lg hover:bg-gray-100 transition"
        >
          再試一次
        </button>
      </div>
    </div>

    <!-- Result -->
    <div
      v-if="result"
      class="result mt-6 p-6 bg-[#1e2021] text-gray-100 rounded-lg space-y-4"
    >
      <h2 class="text-xl font-semibold">預測結果</h2>
      <ul class="space-y-1">
        <li>
          <span class="font-medium">類別：</span>{{ result.prediction }}
        </li>
        <li>
          <span class="font-medium">信心分數：</span>{{ result.confidence }}
        </li>
        <li>
          <span class="font-medium">食物面積比：</span>{{ result.ratio }}
        </li>
      </ul>
      <h3 class="mt-4 text-lg font-semibold">熱量 &amp; 營養素 推測</h3>
      <p>{{ result.gemini }}</p>
      <p>
        總熱量：
        <span class="font-medium">{{ result.total_calories }}</span> 大卡
      </p>
    </div>

    <!-- Error -->
    <div
      v-if="error"
      class="mt-6 p-4 bg-red-100 text-red-800 rounded-lg text-center"
    >
      <h3 class="font-medium">無法辨識，請重新拍攝</h3>
    </div>
  </div>
</template>
  
<script setup>
import { ref } from 'vue'
import axios from 'axios'
import api from '../services/api';

const file        = ref(null)
const previewUrl  = ref(null)
const loading     = ref(false)
const result      = ref(null)
const isDragging  = ref(false)
const imageInput  = ref(null)
const error      = ref(null)

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
    const token = localStorage.getItem('access_token')
    const form = new FormData()
    form.append('image', file.value)
    const { data } = await api.post('api/upload/', form, {
      headers: {
          Authorization: `Bearer ${token}`,
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
  } catch {
    alert('分析失敗，請稍後再試')
  } finally {
    loading.value = false
  }
}

async function saveHistory() {
  if (!result.value) return
  const token = localStorage.getItem('access_token')
  if (!token) return console.warn('⚠️ No token; cannot save history')

  const form = new FormData()
  form.append('image', file.value, file.value.name)
  form.append('detections', JSON.stringify(result.value.detections))
  form.append('total_calories', result.value.total_calories)

  try {
    await axios.post('/api/history/entries/', form, {
      headers: {
        'Authorization': `Bearer ${token}`,     // ← 一定要帶
        'Content-Type': 'multipart/form-data'
      },
      withCredentials: false                  // ← 不送 cookie
    })
  } catch (err) {
    if (err.response?.status === 401) {
      console.warn('⚠️ Unauthorized—please login to save history.')
    }
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
  