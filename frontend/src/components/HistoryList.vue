<template>
  <h1>Your Scan History</h1>
  <div>
    <p v-if="loading">Loading…</p>
    <p v-else-if="!entries.length && !error">No history yet.</p>
    <div v-else>
      <div v-for="e in entries" :key="e.id" class="history-entry">
        <img :src="e.image" :alt="`Scan on ${e.created_at}`" width="180" />
        <p><strong>Total Calories:</strong> {{ e.total_calories }}</p>
        <p><strong>Items:</strong> {{ e.detections.map(d => d.item).join(', ') }}</p>
        <p><em>{{ formatDate(e.created_at) }}</em></p>
      </div>
    </div>
    <p v-if="error" class="text-danger">login to view your history record.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// --- helper to do fetch with JWT header ---
async function authFetch(url, opts = {}) {
  const token = localStorage.getItem('access_token')
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



