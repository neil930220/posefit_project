<template>
    <h1>Your Scan History</h1>
    <div>
      <p v-if="loading">Loading…</p>
      <p v-else-if="!entries.length">No history yet.</p>
      <div v-else>
        <div
          v-for="e in entries"
          :key="e.id"
          class="history-entry"
        >
          <img
            :src="e.image"
            :alt="`Scan on ${e.created_at}`"
            width="180"
          />
          <p><strong>Total Calories:</strong> {{ e.total_calories }}</p>
          <p><strong>Items:</strong> {{ e.detections.map(d => d.item).join(', ') }}</p>
          <p><em>{{ formatDate(e.created_at) }}</em></p>
        </div>
      </div>
      <p v-if="error">Error loading history.</p>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'

  const entries = ref([])
  const loading = ref(true)
  const error = ref(false)
  const isLoaded  = ref(false)       // ← semaphore
  
  function formatDate(s) {
    return new Date(s).toLocaleString()
  }
  
  onMounted(async () => {
    if (isLoaded.value) return       // only fetch once
    loading.value = true
    entries.value = []
    isLoaded.value = true
    try {
      const res = await fetch('/api/history/entries/')
      const data = await res.json()
      entries.value = data
    } catch (e) {
      console.error(e)
      error.value = true
    } finally {
      loading.value = false
    }
  })
  if (import.meta.hot) {
  import.meta.hot.dispose(() => {
    entries.value = []
  })
  }
  </script>
  
  <style scoped>
  .history-entry {
    margin-bottom: 1.5rem;
    /* add your styles… */
  }
  </style>
