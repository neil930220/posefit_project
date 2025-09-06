<template>
    <section
        class="min-h-[calc(100vh-8rem)] flex items-center justify-center relative bg-[url('/assets/pattern.svg')] bg-cover bg-center bg-gray-50"
    >
    <!-- dark overlay -->
    <div class="absolute inset-0 bg-black bg-opacity-75"></div>

    <!-- content -->
    <div class="relative max-w-5xl mx-auto px-6 py-16 text-gray-200 space-y-6">
      <!-- Heading -->
      <h2 class="text-4xl font-bold text-center text-white">
        關於我們
        <span class="block text-lg font-normal text-gray-400 mt-2">— ABOUT US</span>
      </h2>

      <!-- Paragraphs -->
      <p class="leading-relaxed">
        我們是一群熱愛科技與健身的學生，來自台北科技大學資訊與財管系，專注於開發能真正解決生活中問題的創新應用。許多人在健身時因姿勢不正確而導致受傷或效果不佳，尤其是初學者缺乏即時指導與回饋，往往難以持續鍛鍊，我們觀察到這個痛點，於是決定開發一款結合人工智慧姿勢辨識的健身輔助工具——PoseFit。
      </p>

      <p class="leading-relaxed">
        透過整合 OpenPose 等骨架偵測技術，PoseFit 能夠即時分析使用者動作是否標準，並給予回饋與建議。我們希望讓每個人在家也能擁有「專屬教練」，提升運動效率，同時避免不當姿勢造成的風險。
      </p>

      <p class="leading-relaxed">
        除了運動輔助，我們也關注到現代人對健康飲食的重視，因此加入了食物辨識功能。使用者只需拍照上傳餐點圖片，系統便能辨識出食物種類，並透過 AI 模型提供相關營養分析與建議。這項功能旨在幫助使用者更方便地掌握飲食內容，培養正確的營養觀念，打造全面的健康生活方式。
      </p>

      <p class="leading-relaxed">
        這不只是一個科技專題，更是一個讓大眾養成正確運動與飲食習慣的解決方案。我們相信，透過科技與創意的結合，人都能更安全、有效地邁向健康生活。
      </p>
    </div>
  </section>
</template>
