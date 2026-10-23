<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  // [{ name, color, points: [[x, y], ...] }]
  series: { type: Array, required: true },
  xMax: { type: Number, required: true },
  yMin: Number,
  yMax: Number,
  format: { type: Function, default: (v) => Math.round(v) },
  reference: Number, // dashed horizontal line, e.g. 100%
})
const { t } = useI18n()

const W = 720
const H = 260
const L = 56
const R = 16
const T = 16
const B = 28

const range = computed(() => {
  const ys = props.series.flatMap((s) => s.points.map((p) => p[1]))
  if (props.reference != null) ys.push(props.reference)
  let lo = props.yMin ?? Math.min(...ys, 0)
  let hi = props.yMax ?? Math.max(...ys, 1)
  if (hi - lo < 1e-9) hi = lo + 1
  const pad = (hi - lo) * 0.08
  return { lo: props.yMin ?? lo - pad, hi: props.yMax ?? hi + pad }
})
const sx = (x) => L + ((W - L - R) * x) / props.xMax
const sy = (y) => T + (H - T - B) * (1 - (y - range.value.lo) / (range.value.hi - range.value.lo))
const paths = computed(() =>
  props.series.map((s) => ({
    ...s,
    d: s.points.map((p, i) => `${i ? 'L' : 'M'}${sx(p[0]).toFixed(1)},${sy(p[1]).toFixed(1)}`).join(''),
  })),
)
const yTicks = computed(() => {
  const { lo, hi } = range.value
  return Array.from({ length: 5 }, (_, i) => lo + ((hi - lo) * i) / 4)
})
const xTicks = computed(() => Array.from({ length: 5 }, (_, d) => ({ x: d * 660 + 330, label: t(`weekdaysShort.${d}`) })))
</script>

<template>
  <div>
    <svg :viewBox="`0 0 ${W} ${H}`" class="h-auto w-full">
      <g v-for="(y, i) in yTicks" :key="i">
        <line :x1="L" :x2="W - R" :y1="sy(y)" :y2="sy(y)" stroke="#f1f5f9" />
        <text :x="L - 8" :y="sy(y) + 4" font-size="11" fill="#94a3b8" text-anchor="end">{{ format(y) }}</text>
      </g>
      <line v-for="d in 4" :key="`d${d}`" :x1="sx(d * 660)" :x2="sx(d * 660)" :y1="T" :y2="H - B" stroke="#f1f5f9" />
      <text v-for="xt in xTicks" :key="xt.label" :x="sx(xt.x)" :y="H - 8" font-size="11" fill="#94a3b8" text-anchor="middle">{{ xt.label }}</text>
      <line v-if="reference != null" :x1="L" :x2="W - R" :y1="sy(reference)" :y2="sy(reference)" stroke="#cbd5e1" stroke-dasharray="4 4" />
      <path v-for="p in paths" :key="p.name" :d="p.d" fill="none" :stroke="p.color" stroke-width="2" stroke-linejoin="round" />
    </svg>
    <div v-if="series.length > 1" class="mt-2 flex flex-wrap gap-4 text-xs text-slate-600">
      <span v-for="s in series" :key="s.name" class="flex items-center gap-1.5">
        <span class="h-0.5 w-4 rounded" :style="{ background: s.color }" />{{ s.name }}
      </span>
    </div>
  </div>
</template>
