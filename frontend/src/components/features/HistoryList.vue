<template>
  <section class="max-w-3xl mx-auto px-6 py-12">
    <!-- Title -->
    <h1 class="text-3xl font-semibold text-center mb-8">我的紀錄</h1>

    <!-- 1. Loading skeletons -->
    <div v-if="loading" class="space-y-4">
      <div
        v-for="i in 3"
        :key="i"
        class="flex items-center space-x-4 animate-pulse"
      >
        <div class="bg-gray-200 h-24 w-24 rounded"></div>
        <div class="flex-1 space-y-2 py-1">
          <div class="h-4 bg-gray-200 rounded w-3/4"></div>
          <div class="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    </div>

    <!-- 2. Empty state -->
    <div
      v-else-if="!entries.length && !error"
      class="text-center py-16"
    >
      <p class="text-gray-500 mb-6">
        你還沒有任何紀錄！開始你的第一個掃描吧。
      </p>
      <RouterLink
        to="/classify"
        class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        立即掃描
      </RouterLink>
    </div>

    <!-- 3. Real entries -->
    <div v-else class="space-y-6">
      <div
        v-for="e in entries"
        :key="e.id"
        class="flex items-center space-x-4 bg-white shadow rounded-lg p-4"
      >
        <img
          :src="e.image"
          :alt="`Scan on ${formatDate(e.created_at)}`"
          class="h-24 w-24 object-cover rounded"
        />
        <div class="flex-1">
          <p>
            <span class="font-medium">總熱量：</span>{{ e.total_calories }}
          </p>
          <p>
            <span class="font-medium">項目：</span
            >{{ e.detections.map(d => d.item).join(', ') }}
          </p>
          <p class="text-sm text-gray-500">
            {{ formatDate(e.created_at) }}
          </p>
        </div>
      </div>
    </div>

    <!-- 4. Error / not logged-in -->
    <p v-if="error" class="mt-8 text-center text-red-500">
      請
      <RouterLink to="/accounts/login" class="underline hover:text-red-600"
        >登入</RouterLink
      >
      以查看你的紀錄。
    </p>
  </section>
</template> 

<script setup>
import { ref, onMounted } from 'vue'
import { cookieStorage } from '../../utils/cookies'

// --- helper to do fetch with JWT header ---
async function authFetch(url, opts = {}) {
  const token = cookieStorage.getItem('access_token')
  const headers = {
    'Content-Type': 'application/json',
    ...(opts.headers || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
  const res = await fetch(url, { ...opts, headers })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

const entries = ref([])
const loading = ref(false)
const error   = ref(false)

function formatDate(s) {
  return new Date(s).toLocaleString()
}

onMounted(async () => {
  loading.value = true
  error.value   = false
  try {
    // ← make sure this matches your DRF router path!
    entries.value = await authFetch('/api/history/entries/')
  } catch (e) {
      const status = e.response?.status;
      console.error('fetch history failed:', status)
      error.value = true
  } finally {
      loading.value = false
  }
})
</script>

<style scoped>
h1 {
  margin-bottom: 1rem;
  text-align: center;
}

.history-entry {
  border: 1px solid #ccc;
  border-radius: 10px;
  padding: 1rem;
  margin: 1rem 0;
  display: flex;
  align-items: center;
  gap: 1rem;
  background-color: #1e2021;
}

.history-entry img {
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.text-danger {
  color: red;
  text-align: center;
  margin-top: 1rem;
}

p {
  margin: 0.3rem 0;
}
</style>



