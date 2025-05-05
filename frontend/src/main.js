// src/main.js
import { createApp, ref } from 'vue'
import App from './App.vue'
import router from './router'
import CombinedAuth from './components/CombinedAuth.vue'
import HistoryList  from './components/HistoryList.vue'

const app = createApp(App)

// 1️⃣ Create & provide the global loading flag
const loadingApp = ref(false)
app.provide('loadingApp', loadingApp)

// 2️⃣ Add fake-loading via router guards
router.beforeEach((to, from, next) => {
  loadingApp.value = true
  // simulate 300ms “load”
  setTimeout(() => next(), 300)
})

router.afterEach(() => {
  // hide overlay after another 300ms
  setTimeout(() => {
    loadingApp.value = false
  }, 300)
})

// 3️⃣ Register your global components
app.component('CombinedAuth', CombinedAuth)
app.component('HistoryList',  HistoryList)

// 4️⃣ Mount everything
app.use(router)
app.mount('#app')
