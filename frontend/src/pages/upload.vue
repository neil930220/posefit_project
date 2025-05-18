<template>
  <div class="uploader">
    <!-- Drop Zone -->
    <div
      class="drop-zone"
      :class="{ 'is-dragging': isDragging }"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop"
      @click="triggerFileSelect"
    >
      <p v-if="!file">
        Drag & drop an image here, or click to select
      </p>
      <p v-else>
        Selected: {{ file.name }}
      </p>
      <input
        type="file"
        accept="image/*"
        ref="imageInput"
        class="visually-hidden"
        @change="onFilePicked"
      />
    </div>

    <!-- Preview & Actions -->
    <div v-if="file" class="controls">
      <img :src="previewUrl" alt="Preview" class="preview" />
      <div class="buttons">
        <button @click="onSubmit" :disabled="loading">
          {{ loading ? '上傳中…' : '上傳並分析' }}
        </button>
        <button @click="reset" :disabled="loading">再試一次</button>
      </div>
    </div>

    <!-- Result -->
    <div v-if="result" class="result">
      <h2>預測結果</h2>
      <ul>
        <li>類別：<span v-text="result.prediction" /></li>
        <li>信心分數：<span v-text="result.confidence" /></li>
        <li>食物面積比：<span v-text="result.ratio" /></li>
      </ul>
      <h3>熱量 & 營養素 推測</h3>
        <p v-text="result.gemini" />
        <p>總熱量：<span v-text="result.total_calories" /> 大卡</p>
    </div>
    <div v-if="error" class="result">
      <h3>無法辨識請重新拍攝</h3>
    </div>
  </div>
</template>
  
<script setup>
import { ref } from 'vue'
import axios from 'axios'

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
    const { data } = await axios.post('api/upload/', form, {
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
  