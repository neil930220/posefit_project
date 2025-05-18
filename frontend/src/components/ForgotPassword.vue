<template>
  <form @submit.prevent="onSubmit" novalidate>
    <div class="mb-3">
      <label class="form-label">電子郵件</label>
      <input v-model="email" type="email" class="form-control" />
      <div v-if="error" class="text-danger">{{ error }}</div>
    </div>
    <button :disabled="loading" class="btn btn-primary">
      {{ loading ? '傳送中…' : '寄送重設連結' }}
    </button>
    <div v-if="success" class="alert alert-success mt-3">
      已寄出重設連結，請至信箱查看。
    </div>
  </form>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      email: '',
      loading: false,
      success: false,
      error: ''
    }
  },
  methods: {
    async onSubmit() {
      this.loading = true
      this.success = this.error = ''
      try {
        await axios.post('/api/password_reset', { email: this.email })
        this.success = true
      } catch (err) {
        if (err.response?.status === 400) {
          this.error = err.response.data.email?.[0] || '請輸入有效電子郵件'
        } else {
          this.error = '發生錯誤，請稍後再試'
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
