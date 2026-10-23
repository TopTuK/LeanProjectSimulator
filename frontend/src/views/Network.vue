<script setup>
import { computed, inject } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSim } from '../stores/sim.js'

const { t } = useI18n()
const sim = useSim()
const openTask = inject('openTask')

const W = 168
const H = 64
const GAP_X = 56
const GAP_Y = 24
const PAD = 16

const layout = computed(() => {
  const acts = sim.state.activities
  const byLevel = {}
  for (const a of acts) (byLevel[a.level] ??= []).push(a)
  const pos = {}
  let rows = 0
  for (const [lvl, list] of Object.entries(byLevel)) {
    list.sort((a, b) => a.es - b.es || a.no - b.no)
    list.forEach((a, i) => {
      pos[a.no] = { x: PAD + Number(lvl) * (W + GAP_X), y: PAD + i * (H + GAP_Y) }
    })
    rows = Math.max(rows, list.length)
  }
  const levels = Object.keys(byLevel).length
  const edges = []
  for (const a of acts) {
    for (const p of a.preds) {
      const from = pos[p]
      const to = pos[a.no]
      const x1 = from.x + W
      const y1 = from.y + H / 2
      const x2 = to.x
      const y2 = to.y + H / 2
      const mid = (x1 + x2) / 2
      const pred = acts.find((x) => x.no === p)
      edges.push({
        key: `${p}-${a.no}`,
        d: `M${x1},${y1} C${mid},${y1} ${mid},${y2} ${x2 - 6},${y2}`,
        critical: a.critical && pred.critical && Math.abs(pred.ef - a.es) < 1e-9,
      })
    }
  }
  return {
    pos,
    edges,
    width: PAD * 2 + levels * W + (levels - 1) * GAP_X,
    height: PAD * 2 + rows * H + (rows - 1) * GAP_Y,
  }
})

const fill = (a) => (a.status === 'done' ? '#ecfdf5' : a.status === 'active' ? '#eff6ff' : '#ffffff')
const stroke = (a) => (a.critical ? '#ef4444' : '#cbd5e1')
const short = (s) => (s.length > 22 ? `${s.slice(0, 21)}…` : s)
</script>

<template>
  <div class="card mx-auto max-w-7xl overflow-x-auto p-2">
    <svg :width="layout.width" :height="layout.height" class="block" role="img">
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="4" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" fill="#94a3b8" />
        </marker>
        <marker id="arrow-crit" viewBox="0 0 10 10" refX="4" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" fill="#ef4444" />
        </marker>
      </defs>
      <path
        v-for="e in layout.edges"
        :key="e.key"
        :d="e.d"
        fill="none"
        :stroke="e.critical ? '#ef4444' : '#94a3b8'"
        :stroke-width="e.critical ? 2 : 1.25"
        :marker-end="e.critical ? 'url(#arrow-crit)' : 'url(#arrow)'"
      />
      <g v-for="a in sim.state.activities" :key="a.no" class="cursor-pointer" :transform="`translate(${layout.pos[a.no].x},${layout.pos[a.no].y})`" @click="openTask(a.no)">
        <title>{{ a.name }}</title>
        <rect :width="W" :height="H" rx="8" :fill="fill(a)" :stroke="stroke(a)" :stroke-width="a.critical ? 1.75 : 1" />
        <rect :width="W * a.progress" height="3" :y="H - 3" rx="1.5" :fill="a.status === 'done' ? '#10b981' : '#2563eb'" />
        <text x="10" y="20" font-size="11" fill="#94a3b8">{{ a.no }}</text>
        <text x="28" y="20" font-size="12" font-weight="600" fill="#0f172a">{{ short(a.name) }}</text>
        <text x="10" y="40" font-size="11" fill="#64748b">{{ t('network.duration', { n: a.duration }) }}</text>
        <text x="10" y="55" font-size="10" fill="#94a3b8">{{ a.es }}–{{ a.ef }}</text>
        <text v-if="a.slack > 0" :x="W - 10" y="55" font-size="10" fill="#94a3b8" text-anchor="end">{{ t('network.slack', { n: a.slack }) }}</text>
      </g>
    </svg>
  </div>
</template>
