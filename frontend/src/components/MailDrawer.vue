<script setup>
import { computed, inject, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSim } from '../stores/sim.js'
import { useFormat } from '../format.js'
import Icon from './Icon.vue'

const props = defineProps({ focus: Number })
const emit = defineEmits(['close'])
const { t } = useI18n()
const { shortTime } = useFormat()
const sim = useSim()
const openDecision = inject('openDecision')

const selectedId = ref(props.focus)
const selected = computed(() => sim.state.messages.find((m) => m.id === selectedId.value))
const decision = computed(() => sim.state.decisions.find((d) => d.id === selected.value?.decision_id))

watch(
  selected,
  (m) => {
    if (m && !m.read) sim.read(m.id).catch(() => {})
  },
  { immediate: true },
)

const onKey = (e) => e.key === 'Escape' && emit('close')
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
</script>

<template>
  <div class="fixed inset-0 z-30 flex justify-end bg-slate-900/20" @mousedown.self="emit('close')">
    <aside class="flex h-full w-full max-w-md flex-col border-l border-slate-200 bg-white shadow-xl">
      <div class="flex items-center justify-between border-b border-slate-100 px-5 py-4">
        <h2 class="font-semibold text-slate-900">{{ t('mail.title') }}</h2>
        <button class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-50 hover:text-slate-700" @click="emit('close')">
          <Icon name="close" class="h-5 w-5" />
        </button>
      </div>

      <div v-if="selected" class="flex-1 overflow-y-auto px-5 py-4">
        <button class="text-sm text-slate-500 hover:text-slate-800" @click="selectedId = null">← {{ t('mail.back') }}</button>
        <div class="mt-4 flex items-center gap-2 text-xs text-slate-500">
          <Icon :name="selected.channel" class="h-4 w-4" />
          {{ t(`mail.${selected.channel}`) }} · {{ shortTime(selected.time) }}
        </div>
        <h3 class="mt-2 text-lg font-semibold text-slate-900">{{ selected.subject }}</h3>
        <p class="text-sm text-slate-500">{{ selected.sender }}</p>
        <p class="mt-4 text-sm leading-relaxed whitespace-pre-line text-slate-700">{{ selected.body }}</p>
        <button v-if="decision" class="btn btn-primary mt-6" @click="openDecision(decision.id)">
          {{ decision.status === 'open' ? t('mail.openDecision') : t('decision.yourChoice') }}
        </button>
      </div>

      <ul v-else class="flex-1 divide-y divide-slate-100 overflow-y-auto">
        <li v-if="!sim.state.messages.length" class="px-5 py-8 text-center text-sm text-slate-400">{{ t('office.empty') }}</li>
        <li v-for="m in sim.state.messages" :key="m.id">
          <button class="flex w-full gap-3 px-5 py-3 text-left hover:bg-slate-50" @click="selectedId = m.id">
            <Icon :name="m.channel" class="mt-0.5 h-4 w-4 shrink-0" :class="m.read ? 'text-slate-300' : 'text-accent'" />
            <span class="min-w-0 flex-1">
              <span class="flex justify-between gap-2 text-sm">
                <span class="truncate" :class="m.read ? 'text-slate-600' : 'font-semibold text-slate-900'">{{ m.subject }}</span>
                <span class="shrink-0 text-xs text-slate-400">{{ shortTime(m.time) }}</span>
              </span>
              <span class="block truncate text-xs text-slate-500">{{ m.sender }}</span>
            </span>
          </button>
        </li>
      </ul>
    </aside>
  </div>
</template>
