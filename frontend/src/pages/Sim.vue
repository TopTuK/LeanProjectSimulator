<script setup>
import { computed, onBeforeUnmount, provide, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSim } from '../stores/sim.js'
import { setLocale } from '../i18n/index.js'
import { useFormat } from '../format.js'
import { VIEWS } from '../router.js'
import Icon from '../components/Icon.vue'
import ClockButton from '../components/ClockButton.vue'
import MailDrawer from '../components/MailDrawer.vue'
import DecisionModal from '../components/DecisionModal.vue'
import TaskEditor from '../components/TaskEditor.vue'
import EndModal from '../components/EndModal.vue'
import Office from '../views/Office.vue'
import Budget from '../views/Budget.vue'
import Gantt from '../views/Gantt.vue'
import Team from '../views/Team.vue'
import Network from '../views/Network.vue'
import Reports from '../views/Reports.vue'
import Calendar from '../views/Calendar.vue'
import ControlView from '../views/ControlView.vue'
import Help from '../views/Help.vue'

const props = defineProps({ id: String, view: String })
const { t } = useI18n()
const { clockLabel, hhmm } = useFormat()
const sim = useSim()

const COMPONENTS = { office: Office, budget: Budget, gantt: Gantt, team: Team, network: Network, reports: Reports, calendar: Calendar, control: ControlView, help: Help }
const current = computed(() => COMPONENTS[props.view] ?? Office)
const notFound = ref(false)

watch(
  () => props.id,
  async (id) => {
    notFound.value = false
    try {
      const s = await sim.load(id)
      setLocale(s.locale)
    } catch (e) {
      if (e.status === 404) notFound.value = true
    }
  },
  { immediate: true },
)
onBeforeUnmount(() => sim.disconnect())

// overlays
const mailOpen = ref(false)
const mailFocus = ref(null)
const taskNo = ref(null)
const decisionId = ref(null)
const dismissed = ref(new Set())
const endDismissed = ref(false)

function openMail(messageId = null) {
  mailFocus.value = messageId
  mailOpen.value = true
}
function openDecision(id) {
  decisionId.value = id
  mailOpen.value = false
}
function closeDecision() {
  if (decisionId.value != null) dismissed.value.add(decisionId.value)
  decisionId.value = null
}
provide('openTask', (no) => (taskNo.value = no))
provide('openMail', openMail)
provide('openDecision', openDecision)

watch(
  () => sim.openDecisions.map((d) => `${d.id}:${d.postponed}`).join(),
  () => {
    if (decisionId.value != null) return
    const next = sim.openDecisions.find((d) => !d.postponed && !dismissed.value.has(d.id))
    if (next) decisionId.value = next.id
  },
)

const unreadPhone = computed(() => sim.unread.some((m) => m.channel === 'phone'))
const s = computed(() => sim.state)
</script>

<template>
  <div v-if="notFound" class="grid h-full place-items-center">
    <div class="text-center">
      <p class="text-slate-600">{{ t('errors.notFound') }}</p>
      <RouterLink to="/control" class="btn btn-primary mt-4">{{ t('control.newSim') }}</RouterLink>
    </div>
  </div>

  <div v-else-if="s" class="flex h-full">
    <aside class="flex w-16 shrink-0 flex-col border-r border-slate-200 bg-white lg:w-56">
      <div class="border-b border-slate-100 p-3">
        <div class="flex items-center gap-3 rounded-lg bg-slate-900 px-3 py-2 text-white" :title="clockLabel(s.clock)">
          <Icon name="clock" class="h-4 w-4 shrink-0" :class="sim.running ? 'text-emerald-400' : 'text-slate-400'" />
          <span class="hidden min-w-0 leading-tight lg:block">
            <span class="block text-sm font-semibold tabular-nums">{{ hhmm(s.clock) }}</span>
            <span class="block truncate text-[11px] text-slate-400">{{ t(`weekdays.${s.clock.weekday}`) }} · {{ t('weekN', { n: s.clock.week }) }}</span>
          </span>
        </div>
      </div>
      <nav class="flex-1 space-y-0.5 overflow-y-auto p-2">
        <RouterLink
          v-for="v in VIEWS"
          :key="v"
          :to="`/sim/${s.id}/${v}`"
          class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition"
          :class="view === v ? 'bg-accent-soft font-medium text-accent' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'"
          :title="t(`nav.${v}`)"
        >
          <Icon :name="v" class="h-5 w-5 shrink-0" />
          <span class="hidden lg:inline">{{ t(`nav.${v}`) }}</span>
        </RouterLink>
      </nav>
      <div class="hidden border-t border-slate-100 p-4 text-[11px] leading-relaxed text-slate-400 lg:block">
        {{ t('app.name') }}<br />
        {{ t('session') }} {{ s.id.slice(0, 8) }}
      </div>
    </aside>

    <div class="flex min-w-0 flex-1 flex-col">
      <header class="flex items-center gap-3 border-b border-slate-200 bg-white px-4 py-3 sm:px-6">
        <div class="min-w-0 flex-1">
          <h1 class="truncate text-base font-semibold text-slate-900">{{ t(`nav.${view}`) }}</h1>
          <p class="truncate text-xs text-slate-500">
            {{ s.scenario.title }} · <span class="uppercase">{{ s.locale }}</span> · {{ t('badgeDemo') }}
          </p>
        </div>
        <button class="relative rounded-lg p-2 text-slate-500 hover:bg-slate-50 hover:text-slate-900" :class="{ 'text-accent blink': unreadPhone }" :title="t('mail.phone')" @click="openMail()">
          <Icon name="phone" class="h-5 w-5" />
        </button>
        <button class="relative rounded-lg p-2 text-slate-500 hover:bg-slate-50 hover:text-slate-900" :title="t('mail.title')" @click="openMail()">
          <Icon name="mail" class="h-5 w-5" />
          <span v-if="sim.unread.length" class="absolute -top-0.5 -right-0.5 grid h-4 min-w-4 place-items-center rounded-full bg-red-500 px-1 text-[10px] font-semibold text-white">
            {{ sim.unread.length }}
          </span>
        </button>
        <ClockButton />
      </header>

      <p v-if="sim.error" class="border-b border-red-100 bg-red-50 px-6 py-2 text-sm text-red-700">{{ t('errors.generic', { msg: sim.error }) }}</p>

      <main class="min-h-0 flex-1 overflow-auto p-4 sm:p-6">
        <component :is="current" />
      </main>
    </div>

    <MailDrawer v-if="mailOpen" :focus="mailFocus" @close="mailOpen = false" />
    <DecisionModal v-if="decisionId != null" :id="decisionId" @close="closeDecision" />
    <TaskEditor v-if="taskNo != null" :no="taskNo" @close="taskNo = null" />
    <EndModal v-if="sim.ended && !endDismissed && decisionId == null" @close="endDismissed = true" />
  </div>
</template>
