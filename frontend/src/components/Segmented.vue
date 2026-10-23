<script setup>
defineProps({
  options: { type: Array, required: true }, // [{ value, label }]
  disabled: Boolean,
})
const model = defineModel()
</script>

<template>
  <div class="inline-flex flex-wrap rounded-lg border border-slate-200 bg-slate-50 p-0.5 text-sm">
    <button
      v-for="o in options"
      :key="String(o.value)"
      type="button"
      :disabled="disabled"
      class="rounded-md px-3 py-1.5 transition disabled:cursor-not-allowed"
      :class="model === o.value ? 'bg-white font-medium text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-800'"
      @click="model = o.value"
    >
      {{ o.label }}
    </button>
  </div>
</template>
