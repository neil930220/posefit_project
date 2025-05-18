<template>
  <div class="p-4">
    <h1 class="text-2xl font-bold mb-4">開始使用 Start</h1>
    <div class="space-y-4">
      <RouterLink to="/classify" class="block p-4 bg-blue-100 hover:bg-blue-200 rounded shadow">
        食物辨識 Food Recognition →
      </RouterLink>
      <RouterLink to="/start/posture" class="block p-4 bg-green-100 hover:bg-green-200 rounded shadow">
        姿勢訓練 Posture Training →
      </RouterLink>
    </div>

    <!-- Nested route render here -->
    <div class="mt-6">
      <RouterView />
    </div>
  </div>
</template>