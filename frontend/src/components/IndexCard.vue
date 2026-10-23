<script setup>
import { computed } from 'vue'
import { indexTone } from '../format.js'

const props = defineProps({ label: String, value: Number })
const tone = computed(() => indexTone(props.value))
const COLORS = {
  good: { text: 'text-emerald-600', bar: 'bg-emerald-500' },
  warn: { text: 'text-amber-600', bar: 'bg-amber-500' },
  bad: { text: 'text-red-600', bar: 'bg-red-500' },
}
</script>

<template>
  <div class="card p-5">
    <p class="label">{{ label }}</p>
    <p class="mt-2 text-3xl font-semibold tabular-nums" :class="COLORS[tone].text">{{ Math.round(value) }}%</p>
    <div class="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-100">
      <div class="h-full rounded-full transition-all duration-500" :class="COLORS[tone].bar" :style="{ width: `${Math.min(value, 100)}%` }" />
    </div>
  </div>
</template>
