<template>
  <section class="max-w-md mx-auto px-6 py-12">
    <h2 class="text-2xl font-semibold text-center mb-6">忘記密碼</h2>

    <form @submit.prevent="onSubmit" novalidate class="space-y-6">
      <!-- Email field -->
      <div>
        <label class="block text-gray-700 mb-1">電子郵件 *</label>
        <input
          v-model="email"
          type="email"
          placeholder="name@example.com"
          class="w-full border-b border-gray-300 focus:border-gray-600 outline-none py-2"
          required
        />
        <p v-if="error" class="text-red-500 text-sm mt-1">
          {{ error }}
        </p>
      </div>

      <!-- Submit button -->
      <button
        :disabled="loading"
        class="w-full bg-gray-800 text-white py-3 rounded-md font-medium hover:bg-black transition disabled:opacity-50"
      >
        {{ loading ? '傳送中…' : '寄送重設連結' }}
      </button>

      <!-- Success message -->
      <div
        v-if="success"
        class="bg-green-100 border border-green-300 text-green-800 px-4 py-3 rounded-md"
      >
        已寄出重設連結，請至信箱查看。
      </div>
    </form>
  </section>
</template>

<script>
import axios from 'axios'
import api from '../../services/api';

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
        await api.post('/api/password_reset', { email: this.email })
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
