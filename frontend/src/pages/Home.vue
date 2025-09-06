<script setup>
// Import the hero background image
</script>

<template>
  <div class="flex flex-col bg-gray-50">

    <!-- Hero Section -->
    <section
      class="relative h-screen bg-[url('/images/hero-dumbbells.jpg')] bg-cover bg-center"
    >
      <!-- Dark overlay -->
      <div class="absolute inset-0 bg-black bg-opacity-50"></div>

      <!-- Centered content -->
      <div
        class="relative z-10 flex flex-col items-center justify-center h-full text-center px-4"
      >
        <h1 class="text-4xl md:text-6xl font-bold text-white drop-shadow-lg mb-6">
          您身邊的健康小幫手
        </h1>
        <RouterLink
          to="/start"
          class="px-8 py-3 bg-white bg-opacity-75 text-gray-800 font-medium rounded-md hover:bg-opacity-100 transition"
        >
          點選此處
        </RouterLink>
      </div>
    </section>

    <!-- Intro / Call-to-Action Section -->
    <section class="relative py-24 bg-[#1e2021] text-gray-200" style="border-left:0">
      <div
        class="max-w-6xl mx-auto px-6 flex flex-col lg:flex-row items-center gap-12"
      >
        <!-- Left: copy + button -->
        <div class="flex-1 space-y-4">
          <p class="leading-relaxed">
            你是否在運動時常擔心姿勢不正確？
          </p>
          <p class="leading-relaxed">
            你是否難以掌握自己每天吃進了什麼？
          </p>
          <p class="leading-relaxed">
            我們提供健康管理工具，結合人工智慧姿勢辨識與食物影像辨識，幫助你在家就能輕鬆訓練、合理飲食。
          </p>
          <p class="leading-relaxed">
            不論是健身新手還是健康控，每個人都值得擁有專屬的 AI 健康顧問。
          </p>
          <p class="leading-relaxed">
            立即開始，踏出健康生活的第一步！
          </p>
          <RouterLink
            to="/about"
            class="inline-block mt-6 px-6 py-2 border border-gray-400 rounded hover:bg-gray-700 transition"
          >
            關於我們
          </RouterLink>
        </div>

        <!-- Right: background image + blue overlay shapes -->
        <div class="relative flex-1 h-80 lg:h-96">
          <!-- underlying image -->

          <!-- blue translucent skewed shape #1 -->
          <div
            class="absolute bg-blue-500/30 w-1/2 h-2/3 transform -skew-y-12 top-8 right-8"
          ></div>
          <!-- blue translucent skewed shape #2 -->
          <div
            class="absolute bg-blue-500/30 w-1/3 h-1/2 transform skew-y-12 bottom-12 right-16"
          ></div>
        </div>
      </div>
    </section>

  </div>
</template>
