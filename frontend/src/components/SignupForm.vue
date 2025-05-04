<template>
    <form @submit.prevent="onSubmit" novalidate>
      <div class="mb-3">
        <label class="form-label">使用者名稱</label>
        <input v-model="form.username" type="text" class="form-control" />
        <div v-if="errors.username" class="text-danger">{{ errors.username[0] }}</div>
      </div>
  
      <div class="mb-3">
        <label class="form-label">電子郵件</label>
        <input v-model="form.email" type="email" class="form-control" />
        <div v-if="errors.email" class="text-danger">{{ errors.email[0] }}</div>
      </div>
  
      <div class="mb-3">
        <label class="form-label">電話</label>
        <input v-model="form.phone" type="text" class="form-control" />
        <div v-if="errors.phone" class="text-danger">{{ errors.phone[0] }}</div>
      </div>
  
      <div class="mb-3">
        <label class="form-label">生日</label>
        <input v-model="form.birthday" type="date" class="form-control" />
        <div v-if="errors.birthday" class="text-danger">{{ errors.birthday[0] }}</div>
      </div>
  
      <div class="mb-3">
        <label class="form-label">密碼</label>
        <input v-model="form.password1" type="password" class="form-control" />
        <div v-if="errors.password1" class="text-danger">{{ errors.password1[0] }}</div>
      </div>
  
      <div class="mb-3">
        <label class="form-label">再輸入一次密碼</label>
        <input v-model="form.password2" type="password" class="form-control" />
        <div v-if="errors.password2" class="text-danger">{{ errors.password2[0] }}</div>
      </div>
  
      <button :disabled="loading" class="btn btn-primary">
        {{ loading ? '註冊中…' : '註冊' }}
      </button>
      <div v-if="nonFieldError" class="text-danger mt-2">{{ nonFieldError }}</div>
    </form>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    name: 'SignupForm',
    data() {
      return {
        form: {
          username: '',
          email: '',
          phone: '',
          birthday: '',
          password1: '',
          password2: ''
        },
        errors: {},
        nonFieldError: '',
        loading: false,
      };
    },
    methods: {
      getCSRFToken() {
        const match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
      },
      async onSubmit() {
        this.loading = true;
        this.errors = {};
        this.nonFieldError = '';
        try {
          await axios.post('/accounts/signup/', this.form, {
            headers: { 'X-CSRFToken': this.getCSRFToken(), 'X-Requested-With': 'XMLHttpRequest' }
          });
          // 若註冊成功，導向登入頁
          window.location.href = '/accounts/login/';
        } catch (err) {
         console.log('server response:', err.response.data);
          if (err.response && err.response.status === 400) {
            const data = err.response.data;
            // 處理欄位錯誤
            for (const key in data) {
              if (key === '__all__') {
                this.nonFieldError = data[key].join(' ');
              } else {
                this.errors[key] = data[key];
              }
            }
          } else {
            this.nonFieldError = '伺服器錯誤，請稍後再試';
            console.log("result:", this.form);
          }
        } finally {
          this.loading = false;
        }
      }
    }
  };
  </script>
  