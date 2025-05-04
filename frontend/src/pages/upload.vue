<!-- frontend/src/App.vue -->
<template>
    <form @submit.prevent="onSubmit">
      <input type="file" @change="onFileChange" accept="image/*" required ref="imageInput">
      <button :disabled="loading">
        <span v-if="loading">分析中…</span>
        <span v-else>上傳並分析</span>
      </button>
    </form>
  
    <div v-if="!result && !loading">
      <p>請選擇一張圖片並上傳開始分析。</p>
    </div>
    <div v-else-if="loading">
      <p>分析中，請稍候…</p>
    </div>
    <div v-else>
      <h2>預測結果</h2>
    <img :src="result.file_url" style="max-width:400px;">

    <ul>
      <li>類別：<span v-text="result.prediction"></span></li>
      <li>信心分數：<span v-text="result.confidence"></span></li>
      <li>食物面積比：<span v-text="result.ratio"></span></li>
    </ul>

    <h3>熱量 & 營養素 推測</h3>
    <p v-text="result.gemini"></p>

    <p>總熱量：<span v-text="result.total_calories"></span> 大卡</p>

    <button @click="reset()">再試一次</button>
    </div>
  </template>
  
  <script>
  import { ref } from 'vue'
  import axios from 'axios'
  
  export default {
    onFileChange(event) {
      this.file = event.target.files[0];
    },
    methods: {
    reset() {
      // Your reset logic here
      this.file = null;
      this.result = null;
      this.loading = false;
      this.$refs.imageInput.value = ""
    }
    },
    setup() {
      const file     = ref(null)
      const loading  = ref(false)
      const result   = ref(null)
  
      function onFileChange(e) {
        file.value = e.target.files[0]
      }
  
      async function onSubmit() {
        if (!file.value) return
        loading.value = true
        result.value  = null
  
        try {
          const form = new FormData()
          form.append('image', file.value)
          const { data } = await axios.post('/upload/', form, {
            headers: {'X-CSRFToken': document.cookie.match(/csrftoken=([^;]+)/)[1]}
          })
          result.value  = data
          loading.value = false
          saveHistory()
        } catch {
          alert('分析失敗，請稍後再試')
          loading.value = false
        }
      }
  
      async function saveHistory() {
        if (!result.value) return;

        try {
          const form = new FormData();
          form.append('image', file.value, file.value.name);
          form.append('detections', JSON.stringify(result.value.detections));
          form.append('total_calories', result.value.total_calories);
        await axios.post('/api/history/entries/', form, {
          headers: {
            'X-CSRFToken': document.cookie.match(/csrftoken=([^;]+)/)[1]
          },
          withCredentials: true
        });
        } catch (error) {
          if (error.response?.status === 403) {
            console.warn("⚠️ User not logged in; history not saved.");
      // Optionally notify the user
          }
        }
    }
      return { file, loading, result, onFileChange, onSubmit }
    }
  }
  </script>
  