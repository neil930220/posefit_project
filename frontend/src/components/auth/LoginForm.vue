<template>
  <section class="max-w-4xl mx-auto px-6 py-12">
    <div class="grid grid-cols-1 md:grid-cols-2 bg-white shadow-lg rounded-lg overflow-hidden">
      
      <!-- Left: Sign-up prompt -->
      <div class="p-8 border-b md:border-b-0 md:border-r border-gray-200">
        <h2 class="text-2xl font-semibold mb-4">尚未成為會員嗎？</h2>
        <p class="text-gray-600 mb-6">
          此網站上的一些頁面僅供已註冊會員瀏覽。現在就建立帳號以查看此網站上的受限頁面與內容。
        </p>
        <RouterLink
          to="/accounts/signup"
          class="inline-block border border-gray-400 text-gray-700 font-medium px-6 py-2 rounded hover:bg-gray-50 transition"
        >
          創立新帳號
        </RouterLink>
      </div>

      <!-- Right: Login form -->
      <div class="p-8">
        <h2 class="text-2xl font-semibold mb-6">登入</h2>
        <form @submit.prevent="onSubmit" novalidate>
          <div class="mb-4">
            <label class="block text-gray-700 mb-1" for="email">電子郵件 *</label>
            <input
              id="email"
              v-model="form.username"
              type="email"
              class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring focus:border-blue-300"
            />
            <p v-if="errors.username" class="text-red-500 text-sm mt-1">{{ errors.username[0] }}</p>
          </div>

          <div class="mb-6">
            <label class="block text-gray-700 mb-1" for="password">密碼 *</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring focus:border-blue-300"
            />
            <p v-if="errors.password" class="text-red-500 text-sm mt-1">{{ errors.password[0] }}</p>
          </div>

          <button
            :disabled="loading"
            class="w-full bg-gray-800 text-white font-medium py-2 rounded hover:bg-black transition disabled:opacity-50"
          >
            {{ loading ? '登入中…' : '登入' }}
          </button>

          <div class="mt-4 text-center">
            <RouterLink to="/forgot-password" class="text-sm text-gray-600 hover:underline">
              忘記密碼？
            </RouterLink>
          </div>

          <p v-if="nonFieldError" class="text-red-500 text-center mt-4">
            {{ nonFieldError }}
          </p>
        </form>
      </div>

    </div>
  </section>
</template>

<script>
import axios from 'axios';
import api from '../../services/api';

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
        const { data } = await api.post('/api/token/', {
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
