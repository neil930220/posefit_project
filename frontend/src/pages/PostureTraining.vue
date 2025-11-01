<template>
  <div class="min-h-screen bg-gray-900 text-white">
    <!-- Header -->
    <div class="bg-gray-800 p-4">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <RouterLink to="/start" class="text-gray-400 hover:text-white">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
          </RouterLink>
          <h1 class="text-2xl font-bold">姿勢訓練</h1>
        </div>
        
        <div class="flex items-center space-x-4">
          <div v-if="currentSession" class="text-sm">
            <span class="text-gray-400">訓練中:</span>
            <span class="text-green-400">{{ currentSession.session_name }}</span>
          </div>
          <button 
            v-if="!isTraining" 
            @click="startTraining"
            class="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-medium"
          >
            開始訓練
          </button>
          <button 
            v-else
            @click="stopTraining"
            class="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg font-medium"
          >
            結束訓練
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto p-4">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Camera Feed -->
        <div class="lg:col-span-2">
          <div class="bg-gray-800 rounded-lg p-4">
            <h2 class="text-xl font-semibold mb-4">即時姿勢檢測</h2>
            
            <!-- Camera Container -->
            <div class="relative bg-black rounded-lg overflow-hidden" style="aspect-ratio: 16/9;">
              <video 
                ref="videoElement"
                class="w-full h-full object-cover"
                autoplay
                muted
                playsinline
              ></video>
              
              <!-- Overlay for pose visualization -->
              <canvas 
                ref="poseCanvas"
                class="absolute inset-0 w-full h-full"
                :width="canvasWidth"
                :height="canvasHeight"
              ></canvas>
              
              <!-- Loading overlay -->
              <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
                <div class="text-center">
                  <div class="w-8 h-8 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                  <p class="text-white">正在初始化攝影鏡頭...</p>
                </div>
              </div>
              
              <!-- Error overlay -->
              <div v-if="cameraError" class="absolute inset-0 flex items-center justify-center bg-red-900 bg-opacity-50">
                <div class="text-center">
                  <svg class="w-12 h-12 text-red-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 19.5c-.77.833.192 2.5 1.732 2.5z"></path>
                  </svg>
                  <p class="text-red-400">{{ cameraError }}</p>
                  <button @click="initCamera" class="mt-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded">
                    重試
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Controls -->
            <div class="mt-4 flex items-center justify-between">
              <div class="flex items-center space-x-4">
                <button 
                  @click="toggleCamera"
                  class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg"
                >
                  {{ isCameraOn ? '關閉攝影鏡頭' : '開啟攝影鏡頭' }}
                </button>
                
                <button 
                  @click="toggleRealTimeDetection"
                  :disabled="!isCameraOn"
                  class="px-4 py-2 rounded-lg"
                  :class="isRealTimeDetection ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'"
                >
                  {{ isRealTimeDetection ? '停止即時檢測' : '開始即時檢測' }}
                </button>
              </div>
              
              <div class="text-sm text-gray-400">
                幀數: {{ frameCount }}
              </div>
            </div>
          </div>
        </div>

        <!-- Analysis Panel -->
        <div class="space-y-6">
          
          <!-- Current Analysis -->
          <div class="bg-gray-800 rounded-lg p-4">
            <h3 class="text-lg font-semibold mb-4">即時分析</h3>
            
            <div v-if="currentAnalysis" class="space-y-4">
              <!-- Score Display -->
              <div class="text-center">
                <div class="text-3xl font-bold" :class="getScoreColor(currentAnalysis.pose_score)">
                  {{ Math.round(currentAnalysis.pose_score) }}
                </div>
                <div class="text-sm text-gray-400">姿勢分數</div>
              </div>
              
              <!-- Confidence -->
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-400">信心度</span>
                <span class="text-sm font-medium">{{ Math.round(currentAnalysis.confidence * 100) }}%</span>
              </div>
              
              <!-- Progress Bar -->
              <div class="w-full bg-gray-700 rounded-full h-2">
                <div 
                  class="h-2 rounded-full transition-all duration-300"
                  :class="getScoreColor(currentAnalysis.pose_score)"
                  :style="{ width: currentAnalysis.pose_score + '%' }"
                ></div>
              </div>
              
              <!-- Detected Errors -->
              <div v-if="currentAnalysis.detected_errors.length > 0">
                <h4 class="text-sm font-medium text-red-400 mb-2">檢測到的問題</h4>
                <ul class="text-sm space-y-1">
                  <li v-for="error in currentAnalysis.detected_errors" :key="error" class="text-red-300">
                    • {{ error }}
                  </li>
                </ul>
              </div>
              
              <!-- AI Feedback -->
              <div v-if="currentAnalysis.ai_feedback">
                <h4 class="text-sm font-medium text-blue-400 mb-2">AI 建議</h4>
                <p class="text-sm text-gray-300">{{ currentAnalysis.ai_feedback }}</p>
              </div>
            </div>
            
            <div v-else class="text-center text-gray-400 py-8">
              <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
              </svg>
              <p>點擊「分析姿勢」開始檢測</p>
            </div>
          </div>

          <!-- Exercise Selection -->
          <div class="bg-gray-800 rounded-lg p-4">
            <h3 class="text-lg font-semibold mb-4">選擇運動類型</h3>
            
            <select 
              v-model="selectedExerciseType"
              class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
            >
              <option value="">請選擇運動類型</option>
              <option v-for="exercise in exerciseTypes" :key="exercise.id" :value="exercise.id">
                {{ exercise.name }}
              </option>
            </select>
            
            <div v-if="selectedExerciseType" class="mt-4">
              <div class="text-sm text-gray-400 mb-2">運動說明</div>
              <p class="text-sm text-gray-300">
                {{ getExerciseDescription(selectedExerciseType) }}
              </p>
            </div>
          </div>

          <!-- Training Stats -->
          <div v-if="isTraining" class="bg-gray-800 rounded-lg p-4">
            <h3 class="text-lg font-semibold mb-4">訓練統計</h3>
            
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-sm text-gray-400">總次數</span>
                <span class="text-sm font-medium">{{ trainingStats.totalReps }}</span>
              </div>
              
              <div class="flex justify-between">
                <span class="text-sm text-gray-400">平均分數</span>
                <span class="text-sm font-medium">{{ Math.round(trainingStats.averageScore) }}</span>
              </div>
              
              <div class="flex justify-between">
                <span class="text-sm text-gray-400">訓練時間</span>
                <span class="text-sm font-medium">{{ formatDuration(trainingStats.duration) }}</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

// Reactive data
const videoElement = ref(null)
const poseCanvas = ref(null)
const isCameraOn = ref(false)
const isLoading = ref(false)
const cameraError = ref('')
const frameCount = ref(0)
const isTraining = ref(false)
const currentSession = ref(null)
const currentAnalysis = ref(null)
const exerciseTypes = ref([])
const selectedExerciseType = ref('')
const trainingStats = ref({
  totalReps: 0,
  averageScore: 0,
  duration: 0
})

// Canvas dimensions
const canvasWidth = ref(640)
const canvasHeight = ref(480)

// Camera stream
let stream = null
let animationId = null
let isRealTimeDetection = ref(false)
let analysisInterval = null

// Lifecycle
onMounted(async () => {
  await loadExerciseTypes()
  await initCamera()
})

onUnmounted(() => {
  stopCamera()
})

// Methods
const loadExerciseTypes = async () => {
  try {
    const response = await api.get('api/exercise/exercise-types/')
    exerciseTypes.value = response.data
  } catch (error) {
    console.error('Failed to load exercise types:', error)
  }
}

const initCamera = async () => {
  try {
    isLoading.value = true
    cameraError.value = ''
    
    // Request camera access
    stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: 'user'
      }
    })
    
    if (videoElement.value) {
      videoElement.value.srcObject = stream
      await videoElement.value.play()
      
      // Set canvas dimensions
      canvasWidth.value = videoElement.value.videoWidth
      canvasHeight.value = videoElement.value.videoHeight
      
      isCameraOn.value = true
    }
  } catch (error) {
    console.error('Camera initialization failed:', error)
    cameraError.value = '無法存取攝影鏡頭，請檢查權限設定'
  } finally {
    isLoading.value = false
  }
}

const stopCamera = () => {
  stopRealTimeDetection()
  
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
  isCameraOn.value = false
  
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
}

const toggleCamera = () => {
  if (isCameraOn.value) {
    stopRealTimeDetection()
    stopCamera()
  } else {
    initCamera()
  }
}

const toggleRealTimeDetection = () => {
  if (isRealTimeDetection.value) {
    stopRealTimeDetection()
  } else {
    startRealTimeDetection()
  }
}

const startRealTimeDetection = () => {
  if (!isCameraOn.value) {
    alert('請先開啟攝影鏡頭')
    return
  }
  
  console.log('🎬 開始即時檢測...')
  isRealTimeDetection.value = true
  
  // 每 50ms 檢測一次（約 20 FPS），超高流暢度
  analysisInterval = setInterval(() => {
    if (isRealTimeDetection.value && !isProcessing) {
      captureAndAnalyzeFrame()
    } else if (isProcessing) {
      console.log('⏳ Previous request still processing, skipping...')
    }
  }, 50)
  
  // 立即執行第一次檢測
  captureAndAnalyzeFrame()
}

const stopRealTimeDetection = () => {
  isRealTimeDetection.value = false
  
  if (analysisInterval) {
    clearInterval(analysisInterval)
    analysisInterval = null
  }
}

let isProcessing = false  // 防止重複請求

const captureAndAnalyzeFrame = async () => {
  // 檢查是否應該繼續
  if (!isCameraOn.value || !videoElement.value || !isRealTimeDetection.value) {
    console.warn('⚠️ Camera not ready or detection stopped')
    return
  }
  
  // 不阻止執行，而是在處理時跳過
  if (isProcessing) {
    console.log('⏳ Already processing, skipping this frame...')
    return
  }
  
  isProcessing = true
  
  try {
    console.log(`📸 Capturing frame #${frameCount.value}...`)
    
    // Capture frame from video
    const canvas = document.createElement('canvas')
    canvas.width = videoElement.value.videoWidth
    canvas.height = videoElement.value.videoHeight
    
    const ctx = canvas.getContext('2d')
    ctx.drawImage(videoElement.value, 0, 0)
    
    // Convert to base64 - 降低質量以提升速度
    const imageData = canvas.toDataURL('image/jpeg', 0.3)
    
    console.log('📤 Sending to API...')
    
    // Create FormData for multipart/form-data
    const formData = new FormData()
    
    // Convert base64 to Blob
    const base64Data = imageData.split(',')[1]
    const blob = await fetch(imageData).then(r => r.blob())
    formData.append('image', blob, 'frame.jpg')
    formData.append('exercise_type', getExerciseTypeName(selectedExerciseType.value))
    if (currentSession.value?.id) {
      formData.append('session_id', currentSession.value.id)
    }
    formData.append('frame_number', frameCount.value.toString())
    
    // Send to API with FormData
    const response = await api.post('api/exercise/analyze-pose/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 2000  // 2秒超時，快速響應
    })
    
    console.log('✅ Response received:', response.data)
    
    currentAnalysis.value = response.data
    frameCount.value++
    
    // Draw pose on canvas with keypoints only (REALTIME)
    drawPoseOnCanvas(response.data.keypoints)
    
    console.log(`🎯 Detected ${response.data.keypoints?.length || 0} keypoints, Frame: ${frameCount.value}`)
    
    // Update training stats
    if (currentSession.value) {
      trainingStats.value.totalReps = currentSession.value.total_reps || 0
      trainingStats.value.averageScore = currentSession.value.average_score || 0
    }
    
  } catch (error) {
    console.error('❌ Pose analysis failed:', error)
    console.error('Error details:', error.response?.data || error.message)
    
    // 確保幀數增加，即使失敗也要繼續
    frameCount.value++
    console.log('🔄 Continuing detection despite error...')
  } finally {
    isProcessing = false
  }
}

const captureFrame = async () => {
  // 單次分析模式
  await captureAndAnalyzeFrame()
}

const drawPoseOnCanvas = (keypoints) => {
  if (!poseCanvas.value) return
  
  const canvas = poseCanvas.value
  const ctx = canvas.getContext('2d')
  
  // 完全清除 canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // 如果沒有關鍵點，直接返回
  if (!keypoints || keypoints.length === 0) {
    return
  }
  
  // MediaPipe Pose 連接（33個關鍵點）
  const connections = [
    [0, 1], [1, 2], [2, 3], [3, 7],
    [0, 4], [4, 5], [5, 6], [6, 8],
    [9, 10], [11, 12],
    [11, 13], [13, 15], [15, 17], [17, 19], [19, 15],
    [12, 14], [14, 16], [16, 18], [18, 20], [20, 16],
    [15, 21], [16, 22],
    [11, 23], [12, 24],
    [23, 24],
    [23, 25], [24, 26],
    [25, 27], [27, 29], [29, 31], [31, 27],
    [26, 28], [28, 30], [30, 32], [32, 28]
  ]
  
  // 先繪製骨架連接
  connections.forEach(([start, end]) => {
    if (start < keypoints.length && end < keypoints.length) {
      const kp1 = keypoints[start]
      const kp2 = keypoints[end]
      
      if (kp1.confidence > 0.3 && kp2.confidence > 0.3) {
        ctx.beginPath()
        ctx.moveTo(kp1.x * canvas.width, kp1.y * canvas.height)
        ctx.lineTo(kp2.x * canvas.width, kp2.y * canvas.height)
        ctx.strokeStyle = '#FF0080'  // 洋紅色線條
        ctx.lineWidth = 4
        ctx.stroke()
      }
    }
  })
  
  // 再繪製關鍵點（較大、較明顯）
  keypoints.forEach(kp => {
    if (kp.confidence > 0.3) {
      const x = kp.x * canvas.width
      const y = kp.y * canvas.height
      
      // 外圈（較大，亮綠色）
      ctx.beginPath()
      ctx.arc(x, y, 8, 0, 2 * Math.PI)
      ctx.fillStyle = '#00FF00'
      ctx.fill()
      
      // 內圈（較小，深綠色）
      ctx.beginPath()
      ctx.arc(x, y, 4, 0, 2 * Math.PI)
      ctx.fillStyle = '#00AA00'
      ctx.fill()
    }
  })
}

const startTraining = async () => {
  if (!selectedExerciseType.value) {
    alert('請先選擇運動類型')
    return
  }
  
  try {
    const response = await api.post('api/exercise/start-session/', {
      exercise_type_id: selectedExerciseType.value,
      session_name: `${getExerciseTypeName(selectedExerciseType.value)} 訓練`
    })
    
    currentSession.value = response.data
    isTraining.value = true
    trainingStats.value = {
      totalReps: 0,
      averageScore: 0,
      duration: 0
    }
    
  } catch (error) {
    console.error('Failed to start training:', error)
    alert('開始訓練失敗')
  }
}

const stopTraining = async () => {
  if (!currentSession.value) return
  
  try {
    await api.post(`api/exercise/end-session/${currentSession.value.id}/`)
    isTraining.value = false
    currentSession.value = null
    
  } catch (error) {
    console.error('Failed to stop training:', error)
  }
}

const getExerciseTypeName = (id) => {
  const exercise = exerciseTypes.value.find(e => e.id === id)
  return exercise ? exercise.name : '一般運動'
}

const getExerciseDescription = (id) => {
  const exercise = exerciseTypes.value.find(e => e.id === id)
  return exercise ? exercise.description : ''
}

const getScoreColor = (score) => {
  if (score >= 80) return 'text-green-400 bg-green-400'
  if (score >= 60) return 'text-yellow-400 bg-yellow-400'
  return 'text-red-400 bg-red-400'
}

const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
</script>

<style scoped>
/* Additional styles if needed */
</style>
