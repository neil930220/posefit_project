<template>
  <div class="bg-[#1e2021] rounded-lg p-4">
    <div class="flex items-end justify-between">
      <div class="flex-1 mr-4">
        <input
          type="range"
          min="0"
          max="1500"
          step="10"
          class="w-full"
          :value="modelValue"
          @input="onRange"
          :disabled="disabled"
        />
      </div>
      <div class="w-32">
        <label class="block text-sm text-gray-400 mb-1">大卡</label>
        <input
          type="number"
          min="0"
          max="1500"
          step="10"
          class="w-full px-3 py-2 rounded bg-[#2a2b2c] text-gray-100 border border-gray-600 focus:outline-none"
          :value="modelValue"
          @input="onNumber"
          :disabled="disabled"
        />
      </div>
    </div>
    <div class="mt-2 text-sm text-gray-400">拖曳滑桿或輸入數字來猜測總熱量</div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Number, default: 400 },
  disabled: { type: Boolean, default: false }
})
const emit = defineEmits(['update:modelValue'])

function clamp(val) {
  const n = Number(val) || 0
  return Math.max(0, Math.min(1500, Math.round(n)))
}

function onRange(e) {
  emit('update:modelValue', clamp(e.target.value))
}

function onNumber(e) {
  emit('update:modelValue', clamp(e.target.value))
}
</script>


