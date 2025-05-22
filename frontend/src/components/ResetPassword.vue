<template>
  <section class="max-w-md mx-auto px-6 py-12">
    <h2 class="text-2xl font-semibold text-center mb-6">重設密碼</h2>

    <form @submit.prevent="onSubmit" novalidate class="space-y-6">
      <!-- 新密碼 -->
      <div>
        <label class="block text-gray-700 mb-1">新密碼 *</label>
        <input
          v-model="newPassword"
          type="password"
          placeholder="輸入新密碼"
          class="w-full border-b border-gray-300 focus:border-gray-600 outline-none py-2 transition"
          :class="{
            'border-red-500 focus:border-red-500': fieldError('new')
          }"
        />
        <p v-if="fieldError('new')" class="text-red-500 text-sm mt-1">
          {{ fieldError('new') }}
        </p>
      </div>

      <!-- 確認新密碼 -->
      <div>
        <label class="block text-gray-700 mb-1">確認新密碼 *</label>
        <input
          v-model="reNewPassword"
          type="password"
          placeholder="再次輸入新密碼"
          class="w-full border-b border-gray-300 focus:border-gray-600 outline-none py-2 transition"
          :class="{
            'border-red-500 focus:border-red-500': fieldError('re')
          }"
        />
        <p v-if="fieldError('re')" class="text-red-500 text-sm mt-1">
          {{ fieldError('re') }}
        </p>
      </div>

      <!-- Submit -->
      <button
        :disabled="loading"
        class="w-full bg-gray-800 text-white py-3 rounded-md font-medium hover:bg-black transition disabled:opacity-50"
      >
        {{ loading ? '重設中…' : '重設密碼' }}
      </button>

      <!-- Non-field error -->
      <p v-if="nonFieldError" class="text-red-500 text-center text-sm mt-4">
        {{ nonFieldError }}
      </p>
    </form>
  </section>
</template>


<script>
import axios from 'axios'
import api from '../services/api';
export default {
  props: ['uid', 'token'],
  data() {
    return {
      newPassword: '',
      reNewPassword: '',
      loading: false,
      errors: {},         // holds API errors
      nonFieldError: ''   // holds validation / generic errors
    }
  },
  methods: {
    fieldError(which) {
      // helper to read our client or server errors
      if (which === 'new' && this.errors.password)       return this.errors.password[0]
      if (which === 're' && this.errors.re_new_password) return this.errors.re_new_password[0]
      return null
    },

    async onSubmit() {
      this.loading = true
      this.errors = {}
      this.nonFieldError = ''

      // ─── Client-side checks ─────────────────────────────
      if (!this.newPassword || !this.reNewPassword) {
        this.nonFieldError = '請同時填寫「新密碼」與「確認新密碼」'
        this.loading = false
        return
      }
      if (this.newPassword !== this.reNewPassword) {
        this.errors.re_new_password = ['兩次密碼不一致']
        this.loading = false
        return
      }

      // ─── Server call ────────────────────────────────────
      try {
        await api.post('/api/password_reset/confirm', {
          uid: this.uid,
          token: this.token,
          password: this.newPassword
        })
        // redirect to your login page (use whichever route name you’ve defined)
        this.$router.push({ name: 'LoginForm' })
      } catch (err) {
        if (err.response?.status === 400) {
          this.errors = err.response.data
        } else {
          this.nonFieldError = '重設失敗，請確認連結或稍後再試'
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.is-invalid {
  border-color: #dc3545;
}
</style>
