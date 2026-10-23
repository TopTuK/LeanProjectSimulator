<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { api } from '../api.js'
import { useSim } from '../stores/sim.js'
import ControlForm from '../components/ControlForm.vue'

const { t } = useI18n()
const sim = useSim()
const cfg = ref({ ...sim.state.config })
const scenarios = ref([])
onMounted(async () => {
  scenarios.value = await api.scenarios().catch(() => [])
})
</script>

<template>
  <div class="mx-auto max-w-3xl">
    <p class="mb-4 text-sm text-slate-500">{{ t('control.readonly') }}</p>
    <div class="card px-6">
      <ControlForm v-model="cfg" :scenarios="scenarios" readonly />
    </div>
    <div class="mt-6 flex justify-end">
      <RouterLink to="/control" class="btn btn-ghost" @click="sim.disconnect()">{{ t('control.newSim') }}</RouterLink>
    </div>
  </div>
</template>
