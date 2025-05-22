<template>
  <div class="flex flex-col">
    <!-- 食物辨識 Panel -->
    <RouterLink
      to="/classify"
      class="block h-96 lg:h-screen bg-blue-500 hover:bg-blue-600 transition-colors
             flex flex-col items-center justify-center text-center cursor-pointer"
    >
      <h2 class="text-5xl font-bold text-white drop-shadow-md">食物辨識</h2>
      <button class="mt-6 px-8 py-2 bg-white text-gray-800 rounded-lg font-medium">
        Start
      </button>
    </RouterLink>

    <!-- 姿勢訓練 Panel -->
    <RouterLink
      to="/start/posture"
      class="block h-96 lg:h-screen bg-green-500 hover:bg-green-600 transition-colors
             flex flex-col items-center justify-center text-center cursor-pointer"
    >
      <h2 class="text-5xl font-bold text-white drop-shadow-md">姿勢訓練</h2>
      <button class="mt-6 px-8 py-2 bg-white text-gray-800 rounded-lg font-medium">
        Start
      </button>
    </RouterLink>
  </div>
</template>

<script setup>
// no extra logic needed here
</script>

<style>
/* if you want a thin divider line between them on desktop */
@media (min-width: 1024px) {
  .flex-col > a:first-child {
    border-bottom: 1px solid rgba(255,255,255,0.2);
  }
}
</style>