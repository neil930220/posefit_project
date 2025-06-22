<template>
  <div class="max-w-7xl mx-auto px-6 py-12">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
      
      <!-- 食物辨識介紹 -->
      <section>
        <h2 class="text-2xl font-bold mb-2">
          食物辨識介紹
          <span class="text-gray-500 font-normal text-base">— Food Recognition</span>
        </h2>
        <p class="text-gray-700 mb-4">
          你吃下的每一口，都是影響健康的重要關鍵。為了幫助使用者更輕鬆管理飲食，我們導入了食物辨識技術，只需拍照或上傳餐點圖片，系統便能快速辨識出食物種類。
        </p>
        <p class="text-gray-700 mb-4">
          結合 AI 模型與資料庫分析，系統能提供：
        </p>
        <ul class="list-disc list-inside text-gray-700 space-y-2 mb-4">
          <li>食物名稱辨識</li>
          <li>信心度判斷（辨識準確率）</li>
          <li>搭配 Gemini 模型給予營養建議與飲食建議</li>
        </ul>
        <p class="text-gray-700">
          這項功能特別適合希望記錄飲食、養成健康飲食習慣，或正在進行健身、減脂、增肌計畫的使用者。食得健康，才能動得有效！
        </p>
      </section>
      
      <!-- 姿勢辨識介紹 -->
      <section>
        <h2 class="text-2xl font-bold mb-2">
          姿勢辨識介紹
          <span class="text-gray-500 font-normal text-base">— Posture Recognition</span>
        </h2>
        <p class="text-gray-700 mb-4">
          在健身過程中，姿勢正確與否是關鍵因素，不僅影響運動效果，更與受傷風險密切相關。許多初學者因缺乏即時指導，容易出現錯誤動作，導致無法持之以恆，甚至受傷。
        </p>
        <p class="text-gray-700 mb-4">
          我們整合了骨架關鍵點偵測技術（如 OpenPose），打造出即時姿勢辨識系統，能做到以下幾點：
        </p>
        <ul class="list-disc list-inside text-gray-700 space-y-2 mb-4">
          <li>擷取使用者動作影像並即時分析</li>
          <li>辨識動作是否標準（信心度 ≥ 90%）</li>
          <li>搭配 Gemini 模型回饋指導與改善建議</li>
          <li>動作正確者進行評分與歷程記錄</li>
        </ul>
        <p class="text-gray-700">
          無論是深蹲、伏地挺身還是啞鈴訓練，讓 AI 成為你的專屬教練，即時回饋、持續精進！
        </p>
      </section>
      
    </div>
  </div>
</template>

<script setup>
// static content – no additional logic needed here
</script>

<style>
/* if you want a subtle border between columns at larger screens */
@media (min-width: 1024px) {
  section + section {
    border-left: 1px solid #e5e7eb; /* Tailwind's gray-200 */
    padding-left: 2rem;  /* match your gap */
  }
}
</style>
