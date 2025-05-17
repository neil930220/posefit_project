<template>
  <form @submit.prevent="onSubmit" novalidate>
    <div class="mb-3">
      <label class="form-label">新密碼</label>
      <input v-model="newPassword" type="password" class="form-control" />
      <div v-if="errors.new_password" class="text-danger">{{ errors.new_password[0] }}</div>
    </div>
    <div class="mb-3">
      <label class="form-label">確認新密碼</label>
      <input v-model="reNewPassword" type="password" class="form-control" />
      <div v-if="errors.re_new_password" class="text-danger">{{ errors.re_new_password[0] }}</div>
    </div>
    <button :disabled="loading" class="btn btn-primary">
      {{ loading ? '重設中…' : '重設密碼' }}
    </button>
    <div v-if="nonFieldError" class="text-danger mt-2">{{ nonFieldError }}</div>
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
      errors: {},
      nonFieldError: ''
    }
  },
  methods: {
    async onSubmit() {
      this.loading = true
      this.errors = {}
      this.nonFieldError = ''
      try {
        await axios.post('/api/password_reset/confirm/', {
          uid: this.uid,
          token: this.token,
          new_password: this.newPassword,
          re_new_password: this.reNewPassword
        })
        // on success, redirect to login
        this.$router.push({ name: 'Login' })
      } catch (err) {
        if (err.response?.status === 400) {
          this.errors = err.response.data
        } else {
          this.nonFieldError = '重設失敗，請確認連結是否已過期'
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
