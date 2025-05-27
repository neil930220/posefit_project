// src/router.js
import { createRouter, createWebHistory } from 'vue-router'
import Upload from './pages/upload.vue'
import SignupForm from './components/auth/SignupForm.vue'
import LoginForm from './components/auth/LoginForm.vue'
import Home    from './pages/Home.vue'
import HistoryList from './components/features/HistoryList.vue'
import ForgotPassword from './components/auth/ForgotPassword.vue'
import ResetPassword   from './components/auth/ResetPassword.vue'
import StartLayout from './pages/StartLayout.vue'
import features   from './components/pages/features.vue'
import help   from './components/pages/help.vue'
import about   from './components/pages/about.vue'

const routes = [
  { path: '/accounts/signup/',  component: SignupForm,  name: 'SignupForm'  },
  { path: '/accounts/login/',  component: LoginForm,  name: 'LoginForm'  },
  { path: '/',        component: Home    },
  { path: '/history',       component: HistoryList, name: 'History' },
  { path: '/forgot-password',name: 'ForgotPassword',component: ForgotPassword},
  { path: '/reset-password/:uid/:token',name: 'ResetPassword',component: ResetPassword,props: true},
  { path: '/start',component: StartLayout,},
  { path: '/classify',component: Upload,name:'Upload'},
  { path: '/features',component: features,name:'features'},
  { path: '/help',component: help,name:'help'},
  { path: '/about',component: about,name:'about'},
]

const router = createRouter({
  history: createWebHistory(), 
  routes
})

export default router
