<template>
  <form @submit.prevent="onSubmit" novalidate>
    <div class="mb-3">
      <label class="form-label">新密碼</label>
      <input
        v-model="newPassword"
        type="password"
        class="form-control"
        :class="{ 'is-invalid': fieldError('new') }"
      />
      <div v-if="fieldError('new')" class="text-danger">
        {{ fieldError('new') }}
      </div>
    </div>

    <div class="mb-3">
      <label class="form-label">確認新密碼</label>
      <input
        v-model="reNewPassword"
        type="password"
        class="form-control"
        :class="{ 'is-invalid': fieldError('re') }"
      />
      <div v-if="fieldError('re')" class="text-danger">
        {{ fieldError('re') }}
      </div>
    </div>

    <button :disabled="loading" class="btn btn-primary">
      {{ loading ? '重設中…' : '重設密碼' }}
    </button>

    <div v-if="nonFieldError" class="text-danger mt-2">
      {{ nonFieldError }}
    </div>
  </form>
</template>

<script>
import axios from 'axios'
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
        await axios.post('/api/password_reset/confirm', {
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
