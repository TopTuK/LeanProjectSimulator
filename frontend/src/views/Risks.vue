<script setup>
import { computed, inject } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSim } from '../stores/sim.js'
import { useFormat } from '../format.js'
import EffectChips from '../components/EffectChips.vue'

const { t } = useI18n()
const { num, shortTime } = useFormat()
const sim = useSim()
const openDecision = inject('openDecision')
const risks = computed(() => sim.state.risks ?? [])
const open = computed(() => risks.value.filter((r) => r.status === 'open'))
const occurred = computed(() => risks.value.filter((r) => r.status === 'occurred').length)
</script>

<template>
  <div class="mx-auto max-w-6xl space-y-5">
    <section class="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <div class="card p-4"><p class="label">{{ t('risks.identified') }}</p><p class="mt-2 text-2xl font-semibold">{{ risks.length }}</p></div>
      <div class="card p-4"><p class="label">{{ t('risks.open') }}</p><p class="mt-2 text-2xl font-semibold">{{ open.length }}</p></div>
      <div class="card p-4"><p class="label">{{ t('risks.responded') }}</p><p class="mt-2 text-2xl font-semibold">{{ risks.filter((r) => r.response_key).length }}</p></div>
      <div class="card p-4"><p class="label">{{ t('risks.occurred') }}</p><p class="mt-2 text-2xl font-semibold">{{ occurred }}</p></div>
    </section>

    <p class="text-sm text-slate-500">{{ t('risks.hint') }}</p>
    <section v-if="!risks.length" class="card p-8 text-center text-sm text-slate-500" data-test="risks-empty">
      {{ t('risks.empty') }}
    </section>

    <section v-for="r in risks" :key="r.key" class="card p-5" :data-test="`risk-${r.key}`">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div class="min-w-0 flex-1">
          <div class="flex flex-wrap items-center gap-2">
            <h2 class="font-medium text-slate-900">{{ r.name }}</h2>
            <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">{{ r.category }}</span>
            <span
              class="rounded-full px-2 py-0.5 text-xs font-medium"
              :class="r.status === 'occurred' ? 'bg-red-100 text-red-700' : r.status === 'avoided' ? 'bg-emerald-100 text-emerald-700' : r.status === 'open' ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-700'"
            >{{ t(`risks.status.${r.status}`) }}</span>
          </div>
          <p class="mt-2 text-sm leading-relaxed text-slate-600">{{ r.description }}</p>
        </div>
        <button class="btn" :class="r.status === 'open' ? 'btn-primary' : 'btn-ghost'" data-test="open-response" @click="openDecision(r.decision_id)">
          {{ r.status === 'open' ? t('risks.respond') : t('risks.viewResponse') }}
        </button>
      </div>

      <dl class="mt-4 grid gap-3 text-sm sm:grid-cols-3">
        <div><dt class="text-xs text-slate-400">{{ t('risks.probability') }}</dt><dd class="mt-1 font-medium">{{ num(r.probability, 0) }}%</dd></div>
        <div><dt class="text-xs text-slate-400">{{ t('risks.deadline') }}</dt><dd class="mt-1 font-medium">{{ shortTime(r.deadline) }}</dd></div>
        <div v-if="r.response_label"><dt class="text-xs text-slate-400">{{ t('risks.response') }}</dt><dd class="mt-1 font-medium">{{ r.response_label }}</dd></div>
      </dl>
      <EffectChips v-if="r.response_effects" :effects="r.response_effects" class="mt-3" />
      <p v-if="r.outcome" class="mt-3 rounded-lg px-3 py-2 text-sm" :class="r.outcome.occurred ? 'bg-red-50 text-red-700' : 'bg-emerald-50 text-emerald-700'">
        {{ t(r.outcome.occurred ? 'risks.impactApplied' : 'risks.noImpact') }}
      </p>
    </section>
  </div>
</template>
