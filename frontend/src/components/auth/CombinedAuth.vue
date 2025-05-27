<!-- src/components/CombinedAuth.vue -->
<template>
    <div class="card mx-auto" style="max-width: 400px">
      <div class="card-header">
        <ul class="nav nav-tabs card-header-tabs">
          <li class="nav-item">
            <button
              class="nav-link"
              :class="{ active: mode === 'login' }"
              @click="mode = 'login'">
              登入
            </button>
          </li>
          <li class="nav-item">
            <button
              class="nav-link"
              :class="{ active: mode === 'signup' }"
              @click="mode = 'signup'">
              註冊
            </button>
          </li>
        </ul>
      </div>
      <div class="card-body">
        <LoginForm v-if="mode==='login'" />
        <SignupForm v-else />
      </div>
    </div>
  </template>
  
  <script>
  import LoginForm from './LoginForm.vue';
  import SignupForm from './SignupForm.vue';
  export default {
    name: 'CombinedAuth',
    components: { LoginForm, SignupForm },
    data() {
      return { mode: 'login' };
    }
  };
  </script>
    