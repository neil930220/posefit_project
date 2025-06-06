<template>
  <div class="page-wrapper">
    <!-- full-app loading overlay -->
    <transition name="fade">
      <div
        v-if="loadingApp || initialLoading"
        class="fixed inset-0 flex flex-col items-center justify-center z-50"
        style="background-color: #211f21;"
      >
        <!-- Spinner -->
        <div
          class="w-16 h-16 border-4 border-gray-600 border-t-white rounded-full animate-spin"
        ></div>

        <!-- Optional "Loading…" text -->
        <p class="mt-4 text-white text-lg animate-pulse">Loading…</p>
      </div>
    </transition>
    <header>
      <nav class="flex items-center justify-between px-6 py-4 text-white" style="background-color:#211f21">
        
        <!-- 1. Logo + Main Links -->
        <div class="flex items-center space-x-8">
          <!-- Logo -->
          <RouterLink
            to="/"
            class="text-2xl font-bold hover:text-gray-200"
          >
            PostFit
          </RouterLink>

          <!-- Main nav -->
          <RouterLink
            to="/"
            exact
            class="hover:text-gray-200"
            active-class="underline"
          >首頁</RouterLink>

          <RouterLink
            to="/features"
            class="hover:text-gray-200"
            active-class="underline"
          >功能介紹</RouterLink>

          <RouterLink
            to="/start"
            class="hover:text-gray-200"
            active-class="underline"
          >開始使用</RouterLink>

          <RouterLink
            to="/nutrition"
            class="hover:text-gray-200"
            active-class="underline"
          >營養管理</RouterLink>

          <RouterLink
            to="/history"
            class="hover:text-gray-200"
            active-class="underline"
          >我的紀錄</RouterLink>

          <RouterLink
            to="/help"
            class="hover:text-gray-200"
            active-class="underline"
          >幫助中心</RouterLink>

          <RouterLink
            to="/about"
            class="hover:text-gray-200"
            active-class="underline"
          >關於我們</RouterLink>
        </div>

        <!-- 2. Auth / Cart Links -->
        <div class="flex items-center space-x-6">
          <template v-if="user">
            <span class="text-gray-400">歡迎，{{ user.username }}</span>
            <button
              @click="logout"
              class="hover:underline text-red-400"
            >登出</button>
          </template>
          <template v-else>
            <RouterLink
              to="/accounts/login"
              class="hover:text-gray-200"
              active-class="underline"
            >會員登入</RouterLink>
            <RouterLink
              to="/accounts/signup"
              class="hover:text-gray-200"
              active-class="underline"
            >會員註冊</RouterLink>
          </template>

          <!-- Shopping Cart Icon -->
          <RouterLink to="/cart" class="relative hover:text-gray-200">
            <!-- you can swap this SVG for any icon library you prefer -->
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2 9m12-9l2 9m-6-9v9"
              />
            </svg>
            <!-- optional badge -->
            <!-- <span class="absolute -top-1 -right-2 inline-block bg-red-500 text-xs rounded-full px-1">3</span> -->
          </RouterLink>
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

    <footer class="bg-[#1e2021] text-gray-400">
      <div class="max-w-7xl mx-auto px-6 py-12 grid grid-cols-1 md:grid-cols-3 gap-8">

        <!-- Left: Logo & Tagline -->
        <div>
          <h3 class="text-2xl font-semibold text-white mb-4">PostFit</h3>
          <p class="space-y-2">
            <span>用科技打造你的健康生活</span><br/>
            <span>AI 食物辨識・姿勢偵測，讓運動與飲食更有效、更安心。</span>
          </p>
        </div>

        <!-- Center: Info Links -->
        <div>
          <h4 class="text-xl font-semibold text-white mb-4">資訊</h4>
          <ul class="space-y-2">
            <li>
              <RouterLink to="/terms" class="hover:underline">
                使用者條款
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/privacy" class="hover:underline">
                隱私權政策
              </RouterLink>
            </li>
          </ul>
        </div>

        <!-- Right: Contact -->
        <div>
          <h4 class="text-xl font-semibold text-white mb-4">聯絡</h4>
          <ul class="space-y-2">
            <li>
              <a href="mailto:ti1590006@ntut.org.tw" class="hover:underline block">
                電子郵件：ti1590006@ntut.org.tw
              </a>
            </li>
            <li>
              <a href="tel:0981931966" class="hover:underline block">
                電話號碼：0981931966
              </a>
            </li>
          </ul>
        </div>

      </div>

      <!-- Divider -->
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { fetchUser, fetchMessages, doLogout } from './services/api'
import "./assets/style.css"

// injected loading flags
const loadingApp = inject('loadingApp')
const initialLoading = inject('initialLoading')

const user = ref(null);
const router = useRouter();

onMounted(async () => {
  user.value = await fetchUser();
});

async function logout() {
  loadingApp.value = true;
  try {
    await doLogout();
    user.value = null;
    router.push('/');
  } finally {
    const delay = Math.floor(Math.random() * 300) + 200; // random between 200–500ms
    setTimeout(() => {
      loadingApp.value = false;
    }, delay);
  }
}
</script>


<style>
/* fade transition for the overlay */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
