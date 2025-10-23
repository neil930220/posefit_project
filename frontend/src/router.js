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
import NutritionDashboard from './pages/NutritionDashboard.vue'
import PostureTraining from './pages/PostureTraining.vue'
import { cookieStorage } from './utils/cookies'

const routes = [
  { 
    path: '/accounts/signup',  
    component: SignupForm,  
    name: 'SignupForm',
    alias: '/accounts/signup/'
  },
  { 
    path: '/accounts/login',  
    component: LoginForm,  
    name: 'LoginForm',
    alias: '/accounts/login/'
  },
  { path: '/',        component: Home    },
  { path: '/history',       component: HistoryList, name: 'History' },
  { path: '/forgot-password',name: 'ForgotPassword',component: ForgotPassword},
  { path: '/reset-password/:uid/:token',name: 'ResetPassword',component: ResetPassword,props: true},
  { path: '/start',component: StartLayout,},
  { path: '/classify',component: Upload,name:'Upload'},
  { path: '/features',component: features,name:'features'},
  { path: '/help',component: help,name:'help'},
  { path: '/about',component: about,name:'about'},
  { 
    path: '/nutrition', 
    component: NutritionDashboard, 
    name: 'NutritionDashboard',
    meta: { requiresAuth: true }
  },
  { 
    path: '/start/posture', 
    component: PostureTraining, 
    name: 'PostureTraining',
    meta: { requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(), 
  routes
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  console.log('Router navigation:', { from: from.path, to: to.path, name: to.name });
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const hasToken = !!cookieStorage.getItem('access_token');
  const isLoginPage = to.name === 'LoginForm';

  // If trying to access a protected route
  if (requiresAuth) {
    if (!hasToken) {
      console.log('Redirecting to login - no token');
      next('/accounts/login');
      return;
    }
    
    // If we have a token, try to validate it by fetching user data
    try {
      const { fetchUser } = await import('./services/api.js');
      const user = await fetchUser();
      if (!user) {
        console.log('Redirecting to login - invalid token');
        next('/accounts/login');
        return;
      }
    } catch (error) {
      console.log('Redirecting to login - token validation failed');
      next('/accounts/login');
      return;
    }
  }
  
  // If trying to access login page and we have a valid token
  if (isLoginPage && hasToken) {
    try {
      const { fetchUser } = await import('./services/api.js');
      const user = await fetchUser();
      if (user) {
        console.log('Redirecting to home - already authenticated');
    next('/');
        return;
      }
    } catch (error) {
      // If token validation fails, stay on login page
      console.log('Token validation failed, staying on login page');
    }
  }
  
  // Otherwise proceed normally
  console.log('Proceeding to route');
    next();
})

export default router
