<template>
  <form @submit.prevent="onSubmit" novalidate>
    <div class="mb-3">
      <label class="form-label">使用者名稱</label>
      <input v-model="form.username" type="text" class="form-control" />
      <div v-if="errors.username" class="text-danger">{{ errors.username[0] }}</div>
    </div>
    <div class="mb-3">
      <label class="form-label">密碼</label>
      <input v-model="form.password" type="password" class="form-control" />
      <div v-if="errors.password" class="text-danger">{{ errors.password[0] }}</div>
    </div>
    <button :disabled="loading" class="btn btn-success">
      {{ loading ? '登入中…' : '登入' }}
    </button>
        <!-- Forgot password link -->
    <div class="mt-2">
      <router-link to="/forgot-password">忘記密碼？</router-link>
    </div>
    <div v-if="nonFieldError" class="text-danger mt-2">{{ nonFieldError }}</div>
  </form>
</template>

<script>
import axios from 'axios';

export default {
  name: 'LoginForm',
  data() {
    return {
      form: { username: '', password: '' },
      errors: {},
      nonFieldError: '',
      loading: false,
    };
  },
  methods: {
    async onSubmit() {
      this.loading = true;
      this.errors = {};
      this.nonFieldError = '';

      try {
        // 1. POST JSON to token endpoint
        const { data } = await axios.post('/api/token/', {
          username: this.form.username,
          password: this.form.password
        });

        console.log(data)

        // 2. Save tokens
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);

        // 3. Set default Authorization header
        axios.defaults.headers.common.Authorization = `Bearer ${data.access}`;
        // 4. Redirect home
        window.location.href = '/';
      }
    
      catch (err) {
        const status = err.response?.status;
        switch (status) {
          case 401:
            this.nonFieldError = '帳號或密碼錯誤';
            break;
          case 429:
            this.nonFieldError = 'too many attempt,try later';
            break;
          case 400:
            this.errors = err.response.data;
            break;
          default:
            this.nonFieldError = '伺服器錯誤，請稍後再試';
}
}
      finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    // If you already have a token in storage, attach it
    const token = localStorage.getItem('access_token');
    if (token) {
      axios.defaults.headers.common.Authorization = `Bearer ${token}`;
    }
  }
};
</script>
