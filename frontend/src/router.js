// src/router.js
import { createRouter, createWebHistory } from 'vue-router'
import Upload from './pages/upload.vue'
import SignupForm from './components/SignupForm.vue'
import LoginForm from './components/LoginForm.vue'
import Home    from './pages/Home.vue'
import HistoryList from './components/HistoryList.vue'
import ForgotPassword from './components/ForgotPassword.vue'
import ResetPassword   from './components/ResetPassword.vue'

const routes = [
  { path: '/classify',  component: Upload,  name: 'classify'  },
  { path: '/accounts/signup/',  component: SignupForm,  name: 'SignupForm'  },
  { path: '/accounts/login/',  component: LoginForm,  name: 'LoginForm'  },
  { path: '/',        component: Home    },
  { path: '/history',       component: HistoryList, name: 'History' },
  { path: '/forgot-password',name: 'ForgotPassword',component: ForgotPassword},
  {path: '/reset-password/:uid/:token',name: 'ResetPassword',component: ResetPassword,props: true}
]

const router = createRouter({
  history: createWebHistory(), 
  routes
})

export default router
