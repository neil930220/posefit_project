// src/router.js
import { createRouter, createWebHistory } from 'vue-router'
import Upload from './pages/upload.vue'

const routes = [
  { path: '/classify',  component: Upload,  name: 'classify'  },
]

const router = createRouter({
  history: createWebHistory(), 
  routes
})

export default router
