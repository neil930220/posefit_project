// src/router.js
import { createRouter, createWebHistory } from 'vue-router'
import Upload from './pages/upload.vue'
import SignupForm from './components/SignupForm.vue';
import LoginForm from './components/LoginForm.vue';
import Home    from './pages/Home.vue'
import HistoryList from './components/HistoryList.vue';


const routes = [
  { path: '/classify',  component: Upload,  name: 'classify'  },
  { path: '/accounts/signup/',  component: SignupForm,  name: 'SignupForm'  },
  { path: '/accounts/login/',  component: LoginForm,  name: 'LoginForm'  },
  { path: '/',        component: Home    },
  { path: '/history',       component: HistoryList, name: 'History' },

]

const router = createRouter({
  history: createWebHistory(), 
  routes
})

export default router
