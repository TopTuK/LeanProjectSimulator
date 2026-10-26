<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuth } from '../stores/auth.js'
import Icon from './Icon.vue'

defineProps({ next: { type: String, default: '/' } })
const emit = defineEmits(['close'])
const { t } = useI18n()
const auth = useAuth()

// each provider keeps a whisper of its brand colour
const PROVIDERS = [
  { id: 'yandex', color: '#fc3f1d', mark: 'Я' },
  { id: 'vk', color: '#0077ff', mark: 'VK' },
  { id: 'ok', color: '#ee8208', mark: 'OK' },
  { id: 'mail', color: '#005ff9', mark: '@' },
  { id: 'google', color: '#4285f4', mark: 'G' },
]

const card = ref(null)
// move focus into the dialog and hand it back to the opener when it closes
let opener = null

const onKey = (e) => e.key === 'Escape' && emit('close')
onMounted(() => {
  opener = document.activeElement
  card.value?.focus()
  window.addEventListener('keydown', onKey)
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  opener?.focus?.()
})
</script>

<template>
  <div
    class="login-backdrop fixed inset-0 z-40 grid place-items-center bg-slate-900/40 p-4 backdrop-blur-sm"
    @mousedown.self="emit('close')"
  >
    <div
      ref="card"
      class="login-card relative w-full max-w-sm rounded-2xl border border-slate-200/60 bg-white p-8 shadow-2xl shadow-slate-900/10 focus:outline-none"
      role="dialog"
      aria-modal="true"
      aria-labelledby="login-options-title"
      tabindex="-1"
      data-test="login-options"
    >
      <button
        class="absolute right-4 top-4 rounded-lg p-1.5 text-slate-400 transition hover:bg-slate-50 hover:text-slate-700"
        :aria-label="t('task.close')"
        data-test="login-close"
        @click="emit('close')"
      >
        <Icon name="close" class="h-5 w-5" />
      </button>

      <span class="grid h-10 w-10 place-items-center rounded-xl bg-accent text-white">
        <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 16l4-5 3 2.5L18 7" /></svg>
      </span>

      <h2 id="login-options-title" class="mt-5 text-xl font-semibold tracking-tight text-slate-900">{{ t('auth.loginTitle') }}</h2>
      <p class="mt-1 text-sm text-slate-500">{{ t('auth.loginSubtitle') }}</p>

      <div class="mt-7 grid gap-2">
        <button
          v-for="p in PROVIDERS"
          :key="p.id"
          class="group flex w-full items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
          :data-test="`login-${p.id}`"
          @click="auth.login(p.id, next)"
        >
          <span
            class="grid h-8 w-8 shrink-0 place-items-center rounded-full text-xs font-bold"
            :style="{ background: `color-mix(in srgb, ${p.color} 10%, white)`, color: p.color }"
          >
            {{ p.mark }}
          </span>
          {{ t(`auth.providers.${p.id}`) }}
          <svg viewBox="0 0 20 20" class="ml-auto h-4 w-4 text-slate-300 transition group-hover:translate-x-0.5 group-hover:text-slate-500" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 10h11M11 5l5 5-5 5" /></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-backdrop {
  animation: login-fade-in 0.15s ease-out;
}

.login-card {
  animation: login-pop-in 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes login-fade-in {
  from {
    opacity: 0;
  }
}

@keyframes login-pop-in {
  from {
    opacity: 0;
    transform: translateY(8px) scale(0.97);
  }
}
</style>
