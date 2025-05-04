<!-- src/components/LoginForm.vue -->
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
      getCSRFToken() {
        const m = document.cookie.match(/csrftoken=([^;]+)/);
        return m ? m[1] : '';
      },
      async onSubmit() {
        this.loading = true;
        this.errors = {};
        this.nonFieldError = '';
        const payload = new FormData();
        payload.append('username', this.form.username);
        payload.append('password', this.form.password);
        try {
          await axios.post('/accounts/login/', payload, {
            withCredentials: true,
            headers: {
              'X-CSRFToken': this.getCSRFToken(),
              'X-Requested-With': 'XMLHttpRequest'
            }
          });
          // 登入成功，重新導向
          window.location.href = '/'
        } catch (err) {
          if (err.response && err.response.status === 400) {
            const data = err.response.data;
            for (const k in data) {
              if (k === '__all__') this.nonFieldError = data[k][0];
              else this.errors[k] = data[k];
            }
          } else {
            this.nonFieldError = '伺服器錯誤，請稍後再試';
          }
        } finally {
          this.loading = false;
        }
      }
    }
  };
  </script>
  