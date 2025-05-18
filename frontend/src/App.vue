<template>
  <div class="page-wrapper">
    <!-- full-app loading overlay -->
    <div v-if="loadingApp" class="loading-overlay">
      Loading…
    </div>

  <header>
    <nav class="navbar flex justify-between items-center p-4 bg-gray-800 text-white">
      <!-- Left: Main Navigation -->
      <div class="nav-links space-x-4">
        <RouterLink to="/">首頁</RouterLink>
        <RouterLink to="/features">功能介紹</RouterLink>
        <RouterLink to="/start">開始使用</RouterLink>
        <RouterLink to="/help">幫助中心</RouterLink>
        <RouterLink to="/about">關於我們</RouterLink>
      </div>

      <!-- Right: Auth Links -->
      <div class="auth-links space-x-4">
        <template v-if="user">
          <span class="text-gray-300">歡迎，{{ user.username }}</span>
          <RouterLink to="/history">歷史紀錄</RouterLink>
          <button @click="logout" class="text-red-400 hover:underline">登出</button>
        </template>
        <template v-else>
          <RouterLink to="/accounts/login">登入</RouterLink>
          <RouterLink to="/accounts/signup">註冊</RouterLink>
        </template>
      </div>
    </nav>
  </header>
    <!-- flash messages -->
    <transition-group name="fade" tag="div">
      <div v-for="msg in messages" :key="msg" class="messages">
        {{ msg }}
      </div>
    </transition-group>

    <main>
      <!-- your pages here -->
      <RouterView />
    </main>

    <footer>
      © 2025 FoodCam
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { fetchUser, fetchMessages, doLogout } from './services/api'
import "./assets/style.css"

// injected loading flag
const loadingApp = inject('loadingApp')

const user = ref(null);
const router = useRouter();

onMounted(async () => {
  user.value = await fetchUser();
});

async function logout() {
  await doLogout();
  user.value = null;
  router.push('/');
}
</script>

<style>
.loading-overlay {
  position: fixed; top: 0; left: 0;
  width: 100%; height: 100%;
  background: #42484b;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 2em;
  z-index: 9999;
}
/* your other global styles… */
</style>
