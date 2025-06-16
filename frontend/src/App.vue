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
    <header class="relative">
      <nav class="flex items-center justify-between px-8 py-5 text-white shadow-lg border-b border-gray-800" style="background: linear-gradient(135deg, #211f21 0%, #1a1819 100%);">
        
        <!-- 1. Logo + Main Links -->
        <div class="flex items-center">
          <!-- Logo -->
          <RouterLink
            to="/"
            class="text-2xl font-bold hover:text-gray-200 transition-all duration-300 transform hover:scale-105 mr-10"
          >
            <span class="bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">Post</span><span class="text-white">Fit</span>
          </RouterLink>

          <!-- Desktop Navigation -->
          <div class="hidden md:flex items-center space-x-1">
            <RouterLink
              to="/"
              exact
              class="px-4 py-2 rounded-lg hover:bg-gray-700 hover:bg-opacity-60 transition-all duration-200 font-medium relative group"
              active-class="bg-blue-600 bg-opacity-20 text-gray-300"
            >
              首頁
              <span class="absolute bottom-0 left-0 w-0 h-0.5 bg-blue-400 transition-all duration-300 group-hover:w-full"></span>
            </RouterLink>

            <RouterLink
              to="/features"
              class="px-4 py-2 rounded-lg hover:bg-gray-700 hover:bg-opacity-60 transition-all duration-200 font-medium relative group"
              active-class="bg-blue-600 bg-opacity-20 text-gray-300"
            >
              功能介紹
              <span class="absolute bottom-0 left-0 w-0 h-0.5 bg-blue-400 transition-all duration-300 group-hover:w-full"></span>
            </RouterLink>

            <RouterLink
              to="/start"
              class="px-4 py-2 rounded-lg hover:bg-gray-700 hover:bg-opacity-60 transition-all duration-200 font-medium relative group"
              active-class="bg-blue-600 bg-opacity-20 text-gray-300"
            >
              開始使用
              <span class="absolute bottom-0 left-0 w-0 h-0.5 bg-blue-400 transition-all duration-300 group-hover:w-full"></span>
            </RouterLink>

            <RouterLink
              to="/nutrition"
              class="px-4 py-2 rounded-lg hover:bg-gray-700 hover:bg-opacity-60 transition-all duration-200 font-medium relative group"
              active-class="bg-blue-600 bg-opacity-20 text-gray-300"
            >
              營養管理
              <span class="absolute bottom-0 left-0 w-0 h-0.5 bg-blue-400 transition-all duration-300 group-hover:w-full"></span>
            </RouterLink>

            <RouterLink
              to="/history"
              class="px-4 py-2 rounded-lg hover:bg-gray-700 hover:bg-opacity-60 transition-all duration-200 font-medium relative group"
              active-class="bg-blue-600 bg-opacity-20 text-gray-300"
            >
              我的紀錄
              <span class="absolute bottom-0 left-0 w-0 h-0.5 bg-blue-400 transition-all duration-300 group-hover:w-full"></span>
            </RouterLink>

            <RouterLink
              to="/help"
              class="px-4 py-2 rounded-lg hover:bg-gray-700 hover:bg-opacity-60 transition-all duration-200 font-medium relative group"
              active-class="bg-blue-600 bg-opacity-20 text-gray-300"
            >
              幫助中心
              <span class="absolute bottom-0 left-0 w-0 h-0.5 bg-blue-400 transition-all duration-300 group-hover:w-full"></span>
            </RouterLink>

            <RouterLink
              to="/about"
              class="px-4 py-2 rounded-lg hover:bg-gray-700 hover:bg-opacity-60 transition-all duration-200 font-medium relative group"
              active-class="bg-blue-600 bg-opacity-20 text-gray-300"
            >
              關於我們
              <span class="absolute bottom-0 left-0 w-0 h-0.5 bg-blue-400 transition-all duration-300 group-hover:w-full"></span>
            </RouterLink>
          </div>
        </div>

        <!-- 2. Auth / Cart Links -->
        <div class="hidden md:flex items-center space-x-4">
          <template v-if="user">
            <div class="flex items-center space-x-3 px-3 py-2 bg-gray-800 bg-opacity-50 rounded-lg border border-gray-700">
              <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <span class="text-white font-semibold text-xs">{{ user.username.charAt(0).toUpperCase() }}</span>
              </div>
              <span class="text-gray-300 font-medium">{{ user.username }}</span>
            </div>
            <button
              @click="logout"
              class="px-4 py-2 text-red-400 hover:text-red-300 hover:bg-red-900 hover:bg-opacity-20 rounded-lg transition-all duration-200 font-medium border border-transparent hover:border-red-600"
            >登出</button>
          </template>
          <template v-else>
            <RouterLink
              to="/accounts/login"
              class="px-4 py-2 text-gray-300 hover:text-white hover:bg-gray-700 hover:bg-opacity-60 rounded-lg transition-all duration-200 font-medium border border-transparent hover:border-gray-600"
              active-class="bg-blue-600 bg-opacity-20 text-gray-300 border-blue-500"
            >會員登入</RouterLink>
            <RouterLink
              to="/accounts/signup"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all duration-200 font-medium shadow-lg hover:shadow-xl transform hover:scale-105"
              active-class="bg-blue-700"
            >會員註冊</RouterLink>
          </template>

          <!-- Shopping Cart Icon -->
          <RouterLink 
            to="/cart" 
            class="relative p-3 hover:bg-gray-700 hover:bg-opacity-60 rounded-lg transition-all duration-200 group"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-gray-300 group-hover:text-white transition-colors duration-200"
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
          </RouterLink>
        </div>

        <!-- Mobile Menu Button -->
        <button 
          @click="isMobileMenuOpen = !isMobileMenuOpen"
          class="md:hidden p-2 text-white hover:text-gray-200 hover:bg-gray-700 hover:bg-opacity-60 rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              v-if="!isMobileMenuOpen"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"
            />
            <path
              v-else
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </nav>

      <!-- Mobile Menu -->
      <transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="transform -translate-x-full"
        enter-to-class="transform translate-x-0"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="transform translate-x-0"
        leave-to-class="transform -translate-x-full"
      >
        <div
          v-if="isMobileMenuOpen"
          class="fixed inset-0 z-40 md:hidden"
        >
          <!-- Backdrop -->
          <div
            class="fixed inset-0 bg-opacity-20 backdrop-blur-sm"
            @click="isMobileMenuOpen = false"
          ></div>

          <!-- Menu Content -->
          <div class="fixed inset-y-0 left-0 w-72 bg-gradient-to-b from-[#211f21] to-[#1a1819] shadow-2xl border-r border-gray-600">
            <div class="flex flex-col h-full">
              <!-- Header Section -->
              <div class="p-6 border-b border-gray-600 bg-gradient-to-r from-gray-800 to-gray-700">
                <div class="flex items-center justify-between mb-4">
                  <h2 class="text-xl font-bold text-white">PostFit</h2>
                  <button 
                    @click="isMobileMenuOpen = false"
                    class="text-gray-400 hover:text-white transition-colors"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                  </button>
                </div>
                
                <template v-if="user">
                  <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                      <span class="text-white font-semibold text-sm">{{ user.username.charAt(0).toUpperCase() }}</span>
                    </div>
                    <div>
                      <p class="text-white font-medium">{{ user.username }}</p>
                      <button
                        @click="logout"
                        class="text-red-400 hover:text-red-300 text-sm transition-colors"
                      >登出</button>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <div class="space-y-3">
                    <RouterLink
                      to="/accounts/login"
                      class="block w-full text-center bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors font-medium"
                      @click="isMobileMenuOpen = false"
                    >會員登入</RouterLink>
                    <RouterLink
                      to="/accounts/signup"
                      class="block w-full text-center bg-transparent border border-gray-500 hover:border-gray-400 text-gray-300 hover:text-white py-2 px-4 rounded-lg transition-colors"
                      @click="isMobileMenuOpen = false"
                    >會員註冊</RouterLink>
                  </div>
                </template>
              </div>

              <!-- Navigation Links -->
              <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
                <RouterLink
                  to="/"
                  exact
                  class="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-gray-700 hover:bg-opacity-50 transition-all duration-200 group"
                  active-class="bg-blue-600 bg-opacity-20 text-gray-300 font-semibold"
                  @click="isMobileMenuOpen = false"
                >
                  <svg class="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
                  </svg>
                  <span class="text-gray-300 group-hover:text-white transition-colors">首頁</span>
                </RouterLink>

                <RouterLink
                  to="/features"
                  class="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-gray-700 hover:bg-opacity-50 transition-all duration-200 group"
                  active-class="bg-blue-600 bg-opacity-20 text-gray-300 font-semibold"
                  @click="isMobileMenuOpen = false"
                >
                  <svg class="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                  </svg>
                  <span class="text-gray-300 group-hover:text-white transition-colors">功能介紹</span>
                </RouterLink>

                <RouterLink
                  to="/start"
                  class="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-gray-700 hover:bg-opacity-50 transition-all duration-200 group"
                  active-class="bg-blue-600 bg-opacity-20 text-gray-300 font-semibold"
                  @click="isMobileMenuOpen = false"
                >
                  <svg class="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.586a1 1 0 01.707.293l2.414 2.414a1 1 0 00.707.293H15M9 10V9a2 2 0 012-2h2a2 2 0 012 2v1M9 10H7a2 2 0 00-2 2v5a2 2 0 002 2h10a2 2 0 002-2v-5a2 2 0 00-2-2h-2"></path>
                  </svg>
                  <span class="text-gray-300 group-hover:text-white transition-colors">開始使用</span>
                </RouterLink>

                <RouterLink
                  to="/nutrition"
                  class="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-gray-700 hover:bg-opacity-50 transition-all duration-200 group"
                  active-class="bg-blue-600 bg-opacity-20 text-gray-300 font-semibold"
                  @click="isMobileMenuOpen = false"
                >
                  <svg class="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
                  </svg>
                  <span class="text-gray-300 group-hover:text-white transition-colors">營養管理</span>
                </RouterLink>

                <RouterLink
                  to="/history"
                  class="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-gray-700 hover:bg-opacity-50 transition-all duration-200 group"
                  active-class="bg-blue-600 bg-opacity-20 text-gray-300 font-semibold"
                  @click="isMobileMenuOpen = false"
                >
                  <svg class="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <span class="text-gray-300 group-hover:text-white transition-colors">我的紀錄</span>
                </RouterLink>

                <RouterLink
                  to="/help"
                  class="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-gray-700 hover:bg-opacity-50 transition-all duration-200 group"
                  active-class="bg-blue-600 bg-opacity-20 text-gray-300 font-semibold"
                  @click="isMobileMenuOpen = false"
                >
                  <svg class="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <span class="text-gray-300 group-hover:text-white transition-colors">幫助中心</span>
                </RouterLink>

                <RouterLink
                  to="/about"
                  class="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-gray-700 hover:bg-opacity-50 transition-all duration-200 group"
                  active-class="bg-blue-600 bg-opacity-20 text-gray-300 font-semibold"
                  @click="isMobileMenuOpen = false"
                >
                  <svg class="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <span class="text-gray-300 group-hover:text-white transition-colors">關於我們</span>
                </RouterLink>
              </nav>

              <!-- Cart Section -->
              <div class="p-4 border-t border-gray-600 bg-gradient-to-r from-gray-800 to-gray-700">
                <RouterLink
                  to="/cart"
                  class="flex items-center justify-center space-x-3 w-full bg-blue-600 from-blue-600 text-white py-3 px-4 rounded-lg transition-all duration-200 font-medium"
                  @click="isMobileMenuOpen = false"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2 9m12-9l2 9m-6-9v9"></path>
                  </svg>
                  <span>購物車</span>
                </RouterLink>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </header>
    <!-- flash messages -->
    <transition-group name="fade" tag="div">
      <div v-for="msg in messages" :key="msg" class="messages">
        {{ msg }}
      </div>
    </transition-group>

    <main>
      <!-- your pages here -->
      <RouterView @user-updated="handleUserUpdated" />
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
const isMobileMenuOpen = ref(false);

onMounted(async () => {
  try {
    user.value = await fetchUser();
  } catch (err) {
    console.error('Error fetching user:', err);
  } finally {
    initialLoading.value = false;
  }
});

function handleUserUpdated(userData) {
  user.value = userData;
}

async function logout() {
  loadingApp.value = true;
  try {
    await doLogout();
    user.value = null;
    router.push('/');
    isMobileMenuOpen.value = false;
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

/* Prevent body scroll when mobile menu is open */
.mobile-menu-open {
  overflow: hidden;
}
</style>
