// src/main.js
import { createApp, ref } from 'vue'
import axios from 'axios'
import App from './App.vue'
import router from './router'
import CombinedAuth from './components/CombinedAuth.vue'
import HistoryList  from './components/HistoryList.vue'

const _fetch = window.fetch.bind(window)
window.fetch = async (input, init = {}) => {
  const token = localStorage.getItem('access_token')
  init.headers = {
    'Content-Type': 'application/json',
    ...(init.headers || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
  const res = await _fetch(input, init)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res
}

// On app load
const token = localStorage.getItem('access_token')
if (token) {
  axios.defaults.headers.common.Authorization = `Bearer ${token}`
}

// 0️⃣ — Axios JWT setup
//   • If you already logged in, grab the token and set it globally
const initialToken = localStorage.getItem('access_token')
if (initialToken) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${initialToken}`
}

//   • Ensure every new request picks up the freshest token
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})


// 1️⃣ — Create Vue app
const app = createApp(App)

// 2️⃣ — Provide a global loading flag for your fake-loading overlay
const loadingApp = ref(false)
app.provide('loadingApp', loadingApp)

// 3️⃣ — Router guards to simulate a “page load”
router.beforeEach((to, from, next) => {
  loadingApp.value = true
  const delay = Math.floor(Math.random() * 300) + 200 // random between 200–500ms
  setTimeout(() => next(), delay)
})

router.afterEach(() => {
  const delay = Math.floor(Math.random() * 300) + 200 // random between 200–500ms
  setTimeout(() => {
    loadingApp.value = false
  }, delay)
})

// 4️⃣ — Register global components
app.component('CombinedAuth', CombinedAuth)
app.component('HistoryList',  HistoryList)

// 5️⃣ — Use router and mount
app.use(router)
app.mount('#app')
