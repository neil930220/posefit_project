<template>
  <div class="space-y-4">
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-4">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
    </div>

    <!-- Records List -->
    <div v-else-if="records.length > 0" class="space-y-3">
      <div 
        v-for="record in records" 
        :key="record.id"
        class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <div class="flex-1">
          <div class="flex items-center space-x-3">
            <div class="font-semibold text-gray-900">{{ record.weight }}kg</div>
            <div class="text-sm text-gray-500">{{ formatDate(record.date) }}</div>
          </div>
          <div v-if="record.notes" class="text-sm text-gray-600 mt-1">
            {{ record.notes }}
          </div>
          <div class="flex space-x-4 text-xs text-gray-500 mt-1">
            <span v-if="record.bmr">BMR: {{ record.bmr }} kcal</span>
            <span v-if="record.tdee">TDEE: {{ record.tdee }} kcal</span>
          </div>
        </div>
        
        <div class="flex items-center space-x-2">
          <button 
            @click="editRecord(record)"
            class="text-blue-600 hover:text-blue-800 p-1"
            title="編輯"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          
          <button 
            @click="deleteRecord(record)"
            class="text-red-600 hover:text-red-800 p-1"
            title="刪除"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-8">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">暫無記錄</h3>
      <p class="mt-1 text-sm text-gray-500">開始記錄您的體重變化</p>
    </div>

    <!-- Edit Modal -->
    <WeightModal 
      v-if="showEditModal" 
      :weight-record="editingRecord"
      @close="showEditModal = false" 
      @saved="handleRecordSaved"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import nutritionService from '../../services/nutritionService'
import WeightModal from './WeightModal.vue'

export default {
  name: 'RecentWeightRecords',
  components: {
    WeightModal
  },
  emits: ['refresh'],
  setup(props, { emit }) {
    const records = ref([])
    const loading = ref(false)
    const showEditModal = ref(false)
    const editingRecord = ref(null)

    const loadRecords = async () => {
      try {
        loading.value = true
        const data = await nutritionService.getWeightRecords()
        records.value = data.slice(0, 5) // Show only recent 5 records
      } catch (error) {
        console.error('Error loading weight records:', error)
      } finally {
        loading.value = false
      }
    }

    const editRecord = (record) => {
      editingRecord.value = record
      showEditModal.value = true
    }

    const deleteRecord = async (record) => {
      if (!confirm('確定要刪除這筆記錄嗎？')) return

      try {
        await nutritionService.deleteWeightRecord(record.id)
        await loadRecords()
        emit('refresh')
      } catch (error) {
        console.error('Error deleting weight record:', error)
        alert('刪除失敗，請重試')
      }
    }

    const handleRecordSaved = () => {
      showEditModal.value = false
      editingRecord.value = null
      loadRecords()
      emit('refresh')
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-TW', {
        month: 'short',
        day: 'numeric'
      })
    }

    onMounted(() => {
      loadRecords()
    })

    return {
      records,
      loading,
      showEditModal,
      editingRecord,
      editRecord,
      deleteRecord,
      handleRecordSaved,
      formatDate
    }
  }
}
</script> 