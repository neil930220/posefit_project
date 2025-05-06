<template>
  <div class="page-wrapper">
    <!-- full-app loading overlay -->
    <div v-if="loadingApp" class="loading-overlay">
      Loading…
    </div>

    <header>
      <nav class="navbar" style="display: flex; justify-content: space-between; align-items: center;">
        <div class="nav-links">
          <RouterLink to="/">首頁</RouterLink>
          <RouterLink to="/classify">上傳</RouterLink>
        </div>
        <div v-if="user" class="auth-links">
          <span style="color: #e8e6e3;">歡迎，{{ user.username }}</span>
          <button @click="logout">登出</button>
          <RouterLink to="/history">歷史紀錄</RouterLink>
        </div>
        <div v-else class="auth-links">
          <RouterLink to="/accounts/login">登入</RouterLink>
          <RouterLink to="/accounts/signup">註冊</RouterLink>
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
