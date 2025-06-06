<template>
  <div class="space-y-4">
    <!-- Progress Bar -->
    <div>
      <div class="flex justify-between text-sm text-gray-600 mb-2">
        <span>{{ goal.start_weight }}kg</span>
        <span class="font-medium">{{ progressPercentage }}%</span>
        <span>{{ goal.target_weight }}kg</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-3">
        <div 
          class="h-3 rounded-full transition-all duration-300"
          :class="progressBarColor"
          :style="{ width: `${Math.min(progressPercentage, 100)}%` }"
        ></div>
      </div>
    </div>

    <!-- Goal Details -->
    <div class="grid grid-cols-2 gap-4 text-sm">
      <div>
        <p class="text-gray-500">目前體重</p>
        <p class="font-semibold text-lg">{{ goal.current_weight }}kg</p>
      </div>
      <div>
        <p class="text-gray-500">剩餘</p>
        <p class="font-semibold text-lg">{{ goal.remaining_weight }}kg</p>
      </div>
    </div>

    <!-- Timeline -->
    <div class="grid grid-cols-2 gap-4 text-sm">
      <div>
        <p class="text-gray-500">開始日期</p>
        <p class="font-medium">{{ formatDate(goal.start_date) }}</p>
      </div>
      <div>
        <p class="text-gray-500">目標日期</p>
        <p class="font-medium">{{ formatDate(goal.target_date) }}</p>
      </div>
    </div>

    <!-- Status Message -->
    <div class="p-3 rounded-lg" :class="statusMessageClass">
      <p class="text-sm font-medium" :class="statusTextClass">
        {{ statusMessage }}
      </p>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'GoalProgress',
  props: {
    goal: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const progressPercentage = computed(() => {
      return props.goal.progress_percentage || 0
    })

    const progressBarColor = computed(() => {
      const progress = progressPercentage.value
      if (progress >= 100) return 'bg-green-500'
      if (progress >= 75) return 'bg-blue-500'
      if (progress >= 50) return 'bg-yellow-500'
      return 'bg-red-500'
    })

    const statusMessage = computed(() => {
      const progress = progressPercentage.value
      const remaining = props.goal.remaining_weight
      
      if (progress >= 100) {
        return '🎉 恭喜！您已達成目標！'
      } else if (progress >= 75) {
        return `💪 很棒！還差 ${remaining}kg 就達成目標了！`
      } else if (progress >= 50) {
        return `👍 進度良好，繼續保持！還需要 ${remaining}kg`
      } else if (progress >= 25) {
        return `📈 開始有進展了，加油！還需要 ${remaining}kg`
      } else {
        return `🚀 剛開始，堅持下去！還需要 ${remaining}kg`
      }
    })

    const statusMessageClass = computed(() => {
      const progress = progressPercentage.value
      if (progress >= 100) return 'bg-green-50 border border-green-200'
      if (progress >= 75) return 'bg-blue-50 border border-blue-200'
      if (progress >= 50) return 'bg-yellow-50 border border-yellow-200'
      return 'bg-gray-50 border border-gray-200'
    })

    const statusTextClass = computed(() => {
      const progress = progressPercentage.value
      if (progress >= 100) return 'text-green-800'
      if (progress >= 75) return 'text-blue-800'
      if (progress >= 50) return 'text-yellow-800'
      return 'text-gray-800'
    })

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-TW', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    return {
      progressPercentage,
      progressBarColor,
      statusMessage,
      statusMessageClass,
      statusTextClass,
      formatDate
    }
  }
}
</script> 