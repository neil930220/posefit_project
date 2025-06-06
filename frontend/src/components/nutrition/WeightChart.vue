<template>
  <div class="space-y-4">
    <!-- Chart Container -->
    <div v-if="hasData" class="relative">
      <canvas ref="chartRef" width="400" height="200"></canvas>
    </div>
    
    <!-- No Data Message -->
    <div v-else class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">暫無數據</h3>
      <p class="mt-1 text-sm text-gray-500">開始記錄體重以查看進度圖表</p>
    </div>

    <!-- Chart Legend/Stats -->
    <div v-if="hasData" class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
      <div class="bg-blue-50 p-3 rounded-lg">
        <h4 class="text-sm font-medium text-blue-900">起始體重</h4>
        <p class="text-lg font-bold text-blue-600">
          {{ analyticsData.analytics?.starting_weight || '--' }} kg
        </p>
      </div>
      
      <div class="bg-green-50 p-3 rounded-lg">
        <h4 class="text-sm font-medium text-green-900">當前體重</h4>
        <p class="text-lg font-bold text-green-600">
          {{ analyticsData.analytics?.current_weight || '--' }} kg
        </p>
      </div>
      
      <div class="p-3 rounded-lg" :class="weightChangeClass">
        <h4 class="text-sm font-medium" :class="weightChangeTextClass">體重變化</h4>
        <p class="text-lg font-bold" :class="weightChangeTextClass">
          {{ weightChangeDisplay }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import Chart from 'chart.js/auto'

export default {
  name: 'WeightChart',
  props: {
    analyticsData: {
      type: Object,
      required: true,
      default: () => ({
        analytics: {
          current_weight: null,
          starting_weight: null,
          weight_change: 0,
          total_records: 0
        },
        chart_data: {
          dates: [],
          weight: [],
          bmr: [],
          tdee: []
        },
        goal_progress: null,
        date_range: '30d'
      })
    }
  },
  setup(props) {
    const chartRef = ref(null)
    let chart = null

    const hasData = computed(() => {
      return props.analyticsData?.chart_data?.dates?.length > 0
    })

    const weightChange = computed(() => {
      return props.analyticsData?.analytics?.weight_change || 0
    })

    const totalRecords = computed(() => {
      return props.analyticsData?.analytics?.total_records || 0
    })

    const weightChangeDisplay = computed(() => {
      const change = weightChange.value
      if (change === 0) return '無變化'
      const sign = change > 0 ? '+' : ''
      return `${sign}${change} kg`
    })

    const weightChangeClass = computed(() => {
      const change = weightChange.value
      if (change > 0) return 'bg-red-50'
      if (change < 0) return 'bg-green-50'
      return 'bg-gray-50'
    })

    const weightChangeTextClass = computed(() => {
      const change = weightChange.value
      if (change > 0) return 'text-red-900'
      if (change < 0) return 'text-green-900'
      return 'text-gray-900'
    })

    const initChart = () => {
      if (!chartRef.value) return

      const ctx = chartRef.value.getContext('2d')
      
      // Destroy existing chart if it exists
      if (chart) {
        chart.destroy()
      }

      if (!hasData.value) {
        // Create empty chart with message
        chart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: [],
            datasets: []
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              title: {
                display: true,
                text: 'No weight data available'
              }
            }
          }
        })
        return
      }

      const { dates, weight, bmr, tdee } = props.analyticsData.chart_data

      chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: dates,
          datasets: [
            {
              label: 'Weight (kg)',
              data: weight,
              borderColor: 'rgb(75, 192, 192)',
              tension: 0.1,
              yAxisID: 'y'
            },
            {
              label: 'BMR (kcal)',
              data: bmr,
              borderColor: 'rgb(255, 99, 132)',
              tension: 0.1,
              yAxisID: 'y1',
              hidden: true
            },
            {
              label: 'TDEE (kcal)',
              data: tdee,
              borderColor: 'rgb(54, 162, 235)',
              tension: 0.1,
              yAxisID: 'y1',
              hidden: true
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            mode: 'index',
            intersect: false
          },
          scales: {
            y: {
              type: 'linear',
              display: true,
              position: 'left',
              title: {
                display: true,
                text: 'Weight (kg)'
              }
            },
            y1: {
              type: 'linear',
              display: true,
              position: 'right',
              title: {
                display: true,
                text: 'Calories'
              },
              grid: {
                drawOnChartArea: false
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: function(context) {
                  let label = context.dataset.label || ''
                  if (label) {
                    label += ': '
                  }
                  if (context.parsed.y !== null) {
                    label += context.parsed.y.toFixed(2)
                  }
                  return label
                }
              }
            }
          }
        }
      })
    }

    watch(() => props.analyticsData, () => {
      initChart()
    }, { deep: true })

    onMounted(() => {
      initChart()
    })

    return {
      chartRef,
      hasData,
      weightChange,
      totalRecords,
      weightChangeDisplay,
      weightChangeClass,
      weightChangeTextClass
    }
  }
}
</script> 