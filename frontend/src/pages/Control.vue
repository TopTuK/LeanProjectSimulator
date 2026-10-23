<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { api } from '../api.js'
import { useSim } from '../stores/sim.js'
import ControlForm from '../components/ControlForm.vue'

const { t, locale } = useI18n()
const router = useRouter()
const sim = useSim()

const scenarios = ref([])
const cfg = ref({
  locale: locale.value,
  scenario: 'webshop',
  speed: 'demo',
  already_planned: true,
  risk: false,
  raci: false,
  difficulty_cost: 'standard',
  difficulty_schedule: 'standard',
  difficulty_quality: 'standard',
  difficulty_motivation: 'standard',
  difficulty_risk: 'standard',
})

onMounted(async () => {
  try {
    scenarios.value = await api.scenarios()
  } catch (e) {
    sim.error = e.message
  }
})

async function go() {
  const s = await sim.create(cfg.value)
  router.push(`/sim/${s.id}/office`)
}
</script>

<template>
  <div class="mx-auto max-w-3xl px-6 py-10">
    <RouterLink to="/" class="text-sm text-slate-500 hover:text-slate-800">← {{ t('control.back') }}</RouterLink>
    <h1 class="mt-4 text-2xl font-semibold text-slate-900">{{ t('control.title') }}</h1>
    <p class="mt-1 text-sm text-slate-500">{{ t('control.subtitle') }}</p>

    <div class="card mt-6 px-6">
      <ControlForm v-model="cfg" :scenarios="scenarios" />
    </div>

    <p class="mt-4 text-sm text-slate-500">{{ t('control.demoNote') }}</p>
    <p v-if="sim.error" class="mt-4 text-sm text-red-600">{{ t('errors.generic', { msg: sim.error }) }}</p>

    <div class="mt-6 flex justify-end">
      <button class="btn btn-primary px-6 py-3 text-base" :disabled="sim.busy || !scenarios.length" @click="go">
        {{ t('control.save') }}
      </button>
    </div>
  </div>
</template>
