<template>
  <div class="space-y-4">
    <!-- Chart Container -->
    <div v-if="hasData" class="relative">
      <canvas ref="chartCanvas" width="400" height="200"></canvas>
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
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'WeightChart',
  props: {
    analyticsData: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    const chartCanvas = ref(null)
    const chart = ref(null)

    const hasData = computed(() => {
      return props.analyticsData?.chart_data?.dates?.length > 0
    })

    const weightChange = computed(() => {
      return props.analyticsData?.analytics?.weight_change || 0
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

    const createChart = () => {
      if (!chartCanvas.value || !hasData.value) return

      const ctx = chartCanvas.value.getContext('2d')
      const chartData = props.analyticsData.chart_data

      // Destroy existing chart
      if (chart.value) {
        chart.value.destroy()
      }

      chart.value = new Chart(ctx, {
        type: 'line',
        data: {
          labels: chartData.dates,
          datasets: [
            {
              label: '體重 (kg)',
              data: chartData.weight,
              borderColor: '#3B82F6',
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              borderWidth: 2,
              fill: true,
              tension: 0.4,
              pointBackgroundColor: '#3B82F6',
              pointBorderColor: '#ffffff',
              pointBorderWidth: 2,
              pointRadius: 4,
              pointHoverRadius: 6
            },
            {
              label: 'BMR (kcal)',
              data: chartData.bmr,
              borderColor: '#10B981',
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              borderWidth: 2,
              fill: false,
              tension: 0.4,
              pointBackgroundColor: '#10B981',
              pointBorderColor: '#ffffff',
              pointBorderWidth: 2,
              pointRadius: 3,
              pointHoverRadius: 5,
              yAxisID: 'y1'
            },
            {
              label: 'TDEE (kcal)',
              data: chartData.tdee,
              borderColor: '#8B5CF6',
              backgroundColor: 'rgba(139, 92, 246, 0.1)',
              borderWidth: 2,
              fill: false,
              tension: 0.4,
              pointBackgroundColor: '#8B5CF6',
              pointBorderColor: '#ffffff',
              pointBorderWidth: 2,
              pointRadius: 3,
              pointHoverRadius: 5,
              yAxisID: 'y1'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            mode: 'index',
            intersect: false,
          },
          plugins: {
            title: {
              display: true,
              text: '體重與代謝率變化趨勢',
              font: {
                size: 16,
                weight: 'bold'
              }
            },
            legend: {
              position: 'top',
            },
            tooltip: {
              mode: 'index',
              intersect: false,
              callbacks: {
                label: function(context) {
                  let label = context.dataset.label || ''
                  if (label) {
                    label += ': '
                  }
                  if (context.parsed.y !== null) {
                    if (label.includes('kg')) {
                      label += context.parsed.y + ' kg'
                    } else {
                      label += context.parsed.y + ' kcal'
                    }
                  }
                  return label
                }
              }
            }
          },
          scales: {
            x: {
              display: true,
              title: {
                display: true,
                text: '日期'
              },
              grid: {
                display: false
              }
            },
            y: {
              type: 'linear',
              display: true,
              position: 'left',
              title: {
                display: true,
                text: '體重 (kg)'
              },
              grid: {
                color: 'rgba(0, 0, 0, 0.1)'
              }
            },
            y1: {
              type: 'linear',
              display: true,
              position: 'right',
              title: {
                display: true,
                text: '熱量 (kcal)'
              },
              grid: {
                drawOnChartArea: false,
              },
            },
          },
          elements: {
            point: {
              hoverRadius: 8
            }
          }
        }
      })
    }

    watch(() => props.analyticsData, () => {
      nextTick(() => {
        createChart()
      })
    }, { deep: true })

    onMounted(() => {
      nextTick(() => {
        createChart()
      })
    })

    return {
      chartCanvas,
      hasData,
      weightChange,
      weightChangeDisplay,
      weightChangeClass,
      weightChangeTextClass
    }
  }
}
</script> 