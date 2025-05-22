<template>
  <section class="max-w-md mx-auto px-6 py-12 shadow-lg">
    <!-- Heading + subtitle -->
    <h1 class="text-3xl font-semibold text-center mb-2">會員註冊</h1>
    <!-- Form -->
    <form @submit.prevent="onSubmit" novalidate class="space-y-6">
      <!-- Full Name -->
      <div>
        <label class="block text-gray-700 mb-1">全名 *</label>
        <input
          v-model="form.username"
          type="text"
          placeholder="輸入您的全名"
          class="w-full border-b border-gray-300 focus:border-gray-600 outline-none py-2"
        />
        <p v-if="errors.username" class="text-red-500 text-sm mt-1">
          {{ errors.username[0] }}
        </p>
      </div>

      <!-- Email -->
      <div>
        <label class="block text-gray-700 mb-1">電子郵件 *</label>
        <input
          v-model="form.email"
          type="email"
          placeholder="name@example.com"
          class="w-full border-b border-gray-300 focus:border-gray-600 outline-none py-2"
        />
        <p v-if="errors.email" class="text-red-500 text-sm mt-1">
          {{ errors.email[0] }}
        </p>
      </div>

      <!-- Phone -->
      <div>
        <label class="block text-gray-700 mb-1">電話 *</label>
        <input
          v-model="form.phone"
          type="tel"
          placeholder="0912-345-678"
          class="w-full border-b border-gray-300 focus:border-gray-600 outline-none py-2"
        />
        <p v-if="errors.phone" class="text-red-500 text-sm mt-1">
          {{ errors.phone[0] }}
        </p>
      </div>

      <!-- Birthday -->
      <div>
        <label class="block text-gray-700 mb-1">生日 *</label>
        <input
          v-model="form.birthday"
          type="date"
          class="w-full border-b border-gray-300 focus:border-gray-600 outline-none py-2"
        />
        <p v-if="errors.birthday" class="text-red-500 text-sm mt-1">
          {{ errors.birthday[0] }}
        </p>
      </div>

      <!-- Password -->
      <div>
        <label class="block text-gray-700 mb-1">密碼 *</label>
        <input
          v-model="form.password1"
          type="password"
          placeholder="至少 8 個字元"
          class="w-full border-b border-gray-300 focus:border-gray-600 outline-none py-2"
        />
        <p v-if="errors.password1" class="text-red-500 text-sm mt-1">
          {{ errors.password1[0] }}
        </p>
      </div>

      <!-- Confirm Password -->
      <div>
        <label class="block text-gray-700 mb-1">再輸入一次密碼 *</label>
        <input
          v-model="form.password2"
          type="password"
          placeholder="再輸入一次密碼"
          class="w-full border-b border-gray-300 focus:border-gray-600 outline-none py-2"
        />
        <p v-if="errors.password2" class="text-red-500 text-sm mt-1">
          {{ errors.password2[0] }}
        </p>
      </div>

      <!-- Submit -->
      <button
        :disabled="loading"
        class="w-full bg-gray-800 text-white py-3 rounded-md font-medium hover:bg-black transition disabled:opacity-50"
      >
        {{ loading ? '註冊中…' : '註冊' }}
      </button>

      <!-- Non-field errors -->
      <p v-if="nonFieldError" class="text-red-500 text-center text-sm">
        {{ nonFieldError }}
      </p>
    </form>
  </section>
</template>
  
  <script>
  import axios from 'axios';
  import api from '../services/api';

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
          await api.post('/accounts/signup/', this.form, {
            headers: { 
              'X-CSRFToken': this.getCSRFToken(),
              'X-Requested-With': 'XMLHttpRequest',
              'Authorization': ''
            }
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
  