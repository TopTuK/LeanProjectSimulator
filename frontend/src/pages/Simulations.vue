<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuth } from '../stores/auth.js'
import { useSim } from '../stores/sim.js'
import { useFormat } from '../format.js'
import LangSwitch from '../components/LangSwitch.vue'
import Modal from '../components/Modal.vue'

const { t, locale } = useI18n()
const { shortTime } = useFormat()
const router = useRouter()
const auth = useAuth()
const sim = useSim()
const selected = ref(null)

const runningCount = computed(() => sim.sessions.filter((s) => s.status === 'running').length)
const endedCount = computed(() => sim.sessions.filter((s) => s.status === 'ended').length)

onMounted(() => sim.loadSessions().catch(() => {}))

function statusClass(status) {
  return {
    running: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
    paused: 'bg-amber-50 text-amber-700 ring-amber-600/20',
    ended: 'bg-slate-100 text-slate-600 ring-slate-500/20',
    ready: 'bg-blue-50 text-blue-700 ring-blue-600/20',
  }[status] ?? 'bg-slate-100 text-slate-600 ring-slate-500/20'
}

function createdDate(value) {
  return new Intl.DateTimeFormat(locale.value, { dateStyle: 'medium' }).format(new Date(value))
}

async function remove() {
  if (!selected.value) return
  try {
    await sim.remove(selected.value.id)
    selected.value = null
  } catch {}
}

async function logout() {
  await auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-full bg-slate-50">
    <header class="border-b border-slate-200 bg-white">
      <div class="mx-auto flex max-w-6xl items-center gap-4 px-5 py-4 sm:px-8">
        <RouterLink to="/" class="flex items-center gap-2 font-semibold text-slate-900">
          <span class="grid h-8 w-8 place-items-center rounded-lg bg-accent text-white">
            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 16l4-5 3 2.5L18 7" /></svg>
          </span>
          {{ t('app.name') }}
        </RouterLink>
        <div class="ml-auto flex items-center gap-3">
          <span class="hidden text-sm text-slate-500 sm:inline">{{ auth.user?.name }}</span>
          <LangSwitch />
          <button class="text-sm text-slate-500 transition hover:text-slate-900" data-test="logout" @click="logout">{{ t('auth.logout') }}</button>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-6xl px-5 py-8 sm:px-8 sm:py-10">
      <div class="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p class="label">{{ t('app.tagline') }}</p>
          <h1 class="mt-2 text-3xl font-semibold tracking-tight text-slate-950">{{ t('simulations.title') }}</h1>
          <p class="mt-2 max-w-2xl text-sm leading-relaxed text-slate-500">{{ t('simulations.subtitle') }}</p>
        </div>
        <RouterLink to="/control" class="btn btn-primary shrink-0 px-5 py-2.5" data-test="new-simulation">
          <svg viewBox="0 0 20 20" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M10 4v12M4 10h12" /></svg>
          {{ t('control.newSim') }}
        </RouterLink>
      </div>

      <div v-if="sim.sessions.length" class="mt-7 flex flex-wrap gap-x-6 gap-y-2 text-sm text-slate-500" data-test="session-stats">
        <span><strong class="font-semibold text-slate-800">{{ sim.sessions.length }}</strong> {{ t('simulations.total') }}</span>
        <span><strong class="font-semibold text-emerald-700">{{ runningCount }}</strong> {{ t('simulations.runningCount') }}</span>
        <span><strong class="font-semibold text-slate-700">{{ endedCount }}</strong> {{ t('simulations.endedCount') }}</span>
      </div>

      <p v-if="sim.error" class="mt-6 rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert" data-test="sessions-error">
        {{ t('errors.generic', { msg: sim.error }) }}
      </p>

      <div v-if="sim.listBusy" class="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-3" data-test="sessions-loading" aria-busy="true">
        <div v-for="i in 3" :key="i" class="card h-72 animate-pulse p-5">
          <div class="h-5 w-2/3 rounded bg-slate-200" />
          <div class="mt-4 h-3 w-1/3 rounded bg-slate-100" />
          <div class="mt-8 grid grid-cols-2 gap-4"><div v-for="j in 4" :key="j" class="h-12 rounded bg-slate-100" /></div>
        </div>
      </div>

      <section v-else-if="!sim.sessions.length" class="card mt-8 flex flex-col items-center px-6 py-16 text-center" data-test="sessions-empty">
        <span class="grid h-14 w-14 place-items-center rounded-2xl bg-accent-soft text-accent">
          <svg viewBox="0 0 24 24" class="h-7 w-7" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19V5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v14M2 19h20M8 7h8M8 11h5" /></svg>
        </span>
        <h2 class="mt-5 text-lg font-semibold text-slate-900">{{ t('simulations.emptyTitle') }}</h2>
        <p class="mt-2 max-w-md text-sm leading-relaxed text-slate-500">{{ t('simulations.emptyLead') }}</p>
        <RouterLink to="/control" class="btn btn-primary mt-6">{{ t('simulations.createFirst') }}</RouterLink>
      </section>

      <div v-else class="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-3" data-test="session-list">
        <article v-for="s in sim.sessions" :key="s.id" class="card flex min-w-0 flex-col p-5 transition hover:border-slate-300 hover:shadow-sm" :data-test="`session-${s.id}`">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <h2 class="truncate text-base font-semibold text-slate-900" :title="s.scenario.title">{{ s.scenario.title }}</h2>
              <p class="mt-1 text-xs text-slate-400">{{ t('session') }} {{ s.id.slice(0, 8) }} · {{ createdDate(s.created_at) }}</p>
            </div>
            <span class="shrink-0 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset" :class="statusClass(s.status)" :data-test="`status-${s.id}`">
              {{ t(`status.${s.status}`) }}
            </span>
          </div>

          <dl class="mt-5 grid grid-cols-2 gap-x-4 gap-y-4 text-sm">
            <div><dt class="text-xs text-slate-400">{{ t('control.mode') }}</dt><dd class="mt-1 font-medium text-slate-700">{{ t(`mode.${s.config.mode || 'demo'}`) }}</dd></div>
            <div><dt class="text-xs text-slate-400">{{ t('control.speed') }}</dt><dd class="mt-1 font-medium text-slate-700">{{ t(`speed.${s.config.speed}`) }}</dd></div>
            <div><dt class="text-xs text-slate-400">{{ t('control.risk') }}</dt><dd class="mt-1 font-medium text-slate-700">{{ s.config.risk ? t('yes') : t('no') }}</dd></div>
            <div><dt class="text-xs text-slate-400">{{ t('simulations.clock') }}</dt><dd class="mt-1 font-medium text-slate-700">{{ t('weekN', { n: s.clock.week }) }} · {{ shortTime(s.clock) }}</dd></div>
          </dl>

          <div class="mt-5">
            <div class="flex items-center justify-between text-xs"><span class="text-slate-400">{{ t('office.progress') }}</span><span class="font-semibold text-slate-700">{{ s.completion }}%</span></div>
            <div class="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-100"><div class="h-full rounded-full bg-accent transition-all" :style="{ width: `${s.completion}%` }" /></div>
          </div>

          <div class="mt-auto flex items-center gap-2 border-t border-slate-100 pt-4">
            <RouterLink :to="`/sim/${s.id}/office`" class="btn btn-primary flex-1" :data-test="`open-${s.id}`">{{ t('simulations.open') }}</RouterLink>
            <button class="btn btn-ghost border-red-100 px-3 text-red-600 hover:border-red-200 hover:bg-red-50" :disabled="sim.deleting === s.id" :aria-label="t('simulations.deleteLabel', { title: s.scenario.title })" :data-test="`delete-${s.id}`" @click="selected = s">
              <svg viewBox="0 0 20 20" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 5h12M8 5V3h4v2M5 5l1 12h8l1-12M8 8v6M12 8v6" /></svg>
              <span class="hidden sm:inline">{{ sim.deleting === s.id ? t('simulations.deleting') : t('simulations.delete') }}</span>
            </button>
          </div>
        </article>
      </div>
    </main>

    <Modal v-if="selected" :title="t('simulations.deleteTitle')" @close="selected = null">
      <p class="text-sm leading-relaxed text-slate-600" data-test="delete-confirmation">
        {{ t('simulations.deleteWarning', { title: selected.scenario.title }) }}
      </p>
      <p v-if="selected.status === 'running'" class="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800">{{ t('simulations.deleteRunning') }}</p>
      <template #footer>
        <button class="btn btn-ghost" data-test="delete-cancel" @click="selected = null">{{ t('team.cancel') }}</button>
        <button class="btn bg-red-600 text-white hover:bg-red-700" :disabled="sim.deleting === selected.id" data-test="delete-confirm" @click="remove">
          {{ sim.deleting === selected.id ? t('simulations.deleting') : t('simulations.deleteConfirm') }}
        </button>
      </template>
    </Modal>
  </div>
</template>
