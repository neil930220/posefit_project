<!-- frontend/src/App.vue -->
<template>
  <div class="page-wrapper">
    <!-- full‐app loading overlay -->
    <div v-if="loadingApp" class="loading-overlay">
      Loading…
    </div>

    <header>
      <h1>FoodCam 🍱</h1>
      <nav style="display: flex; justify-content: space-between; align-items: center;" class="navbar">
      <div class="nav-links">
          <RouterLink to="/">首頁</RouterLink>
          <RouterLink to="/classify">上傳</RouterLink>
      </div> 
       <div v-if="user" class="auth-links">
        <span>歡迎，{{ user.username }}</span>
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
      <div
        v-for="msg in messages"
        :key="msg"
        class="messages"
      >
        {{ msg }}
      </div>
    </transition-group>

    <main >
      <!-- your pages here -->
      <RouterView />
    </main>

    <footer>
      © 2025 FoodCam
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter }   from 'vue-router'
import { fetchUser, fetchMessages, doLogout } from './services/api'

const loadingApp = ref(true)
const user       = ref(null)
const messages   = ref([])

const router = useRouter()

onMounted(async () => {
  // maybe fetch auth state & messages
  user.value     = await fetchUser()
  messages.value = await fetchMessages()
  loadingApp.value = false
})

function logout() {
  doLogout().then(() => {
    user.value = null
    router.push('/login')
  })
}
</script>
<style>
.loading-overlay {
  position: fixed; top: 0; left: 0;
  width: 100%; height: 100%;
  background: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 2em;
  z-index: 9999;
}
/* your other global styles… */
</style>
