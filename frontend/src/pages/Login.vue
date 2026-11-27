<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuth } from '../stores/auth.js'
import LangSwitch from '../components/LangSwitch.vue'
import LoginOptions from '../components/LoginOptions.vue'
import heroImg from '../assets/landing-hero.jpg'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const auth = useAuth()
const next = computed(() => {
  const value = route.query.next
  return typeof value === 'string' && /^\/(?![/\\])/.test(value) ? value : '/simulations'
})
const authError = computed(() => route.query.auth_error !== undefined)

onMounted(async () => {
  if (await auth.fetch()) router.replace(next.value)
})
</script>

<template>
  <div class="grid min-h-full bg-white lg:grid-cols-[minmax(0,1.1fr)_minmax(28rem,0.9fr)]">
    <section class="login-hero relative hidden overflow-hidden bg-slate-950 px-12 py-10 text-white lg:flex lg:flex-col">
      <RouterLink to="/" class="relative z-10 flex w-fit items-center gap-3 font-semibold">
        <span class="grid h-9 w-9 place-items-center rounded-xl bg-accent text-white shadow-lg shadow-blue-950/30">
          <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 16l4-5 3 2.5L18 7" /></svg>
        </span>
        <span class="text-lg">{{ t('app.name') }}</span>
      </RouterLink>

      <div class="relative z-10 my-auto max-w-xl py-12">
        <p class="text-xs font-semibold tracking-[0.2em] text-blue-300 uppercase">{{ t('app.tagline') }}</p>
        <h1 class="mt-5 text-4xl font-semibold tracking-tight text-balance xl:text-5xl">{{ t('auth.heroTitle') }}</h1>
        <p class="mt-5 max-w-lg text-base leading-relaxed text-slate-300">{{ t('auth.heroLead') }}</p>
        <img :src="heroImg" alt="" class="mt-10 w-full max-w-lg rounded-2xl border border-white/10 shadow-2xl shadow-black/20" />
      </div>

      <p class="relative z-10 text-xs text-slate-500">{{ t('auth.heroFootnote') }}</p>
    </section>

    <main class="flex min-h-full flex-col px-6 py-5 sm:px-10 lg:px-12">
      <header class="flex items-center justify-between gap-4">
        <RouterLink to="/" class="flex items-center gap-2 font-semibold text-slate-900 lg:hidden">
          <span class="grid h-8 w-8 place-items-center rounded-lg bg-accent text-white">
            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 16l4-5 3 2.5L18 7" /></svg>
          </span>
          {{ t('app.name') }}
        </RouterLink>
        <RouterLink to="/" class="hidden text-sm text-slate-500 transition hover:text-slate-900 lg:inline-flex">← {{ t('control.back') }}</RouterLink>
        <LangSwitch />
      </header>

      <div class="mx-auto flex w-full max-w-md flex-1 flex-col justify-center py-12">
        <div class="mb-8 lg:hidden">
          <p class="label">{{ t('app.tagline') }}</p>
        </div>
        <div>
          <span class="grid h-11 w-11 place-items-center rounded-xl bg-accent-soft text-accent">
            <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3" /></svg>
          </span>
          <h2 class="mt-6 text-3xl font-semibold tracking-tight text-slate-950">{{ t('auth.loginTitle') }}</h2>
          <p class="mt-2 text-sm leading-relaxed text-slate-500">{{ t('auth.loginSubtitle') }}</p>
        </div>

        <p v-if="authError" class="mt-6 rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700" data-test="auth-error" role="alert">
          {{ t('auth.error') }}
        </p>

        <LoginOptions class="mt-8" :next="next" />

        <div class="mt-8 flex items-start gap-3 border-t border-slate-100 pt-6 text-xs leading-relaxed text-slate-400">
          <svg viewBox="0 0 24 24" class="mt-0.5 h-4 w-4 shrink-0" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="10" width="16" height="11" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3" /></svg>
          <p>{{ t('auth.privacy') }}</p>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.login-hero::before,
.login-hero::after {
  position: absolute;
  border-radius: 9999px;
  content: '';
  filter: blur(2px);
  pointer-events: none;
}

.login-hero::before {
  top: -12rem;
  right: -10rem;
  width: 32rem;
  height: 32rem;
  background: radial-gradient(circle, rgb(37 99 235 / 0.24), transparent 68%);
}

.login-hero::after {
  bottom: -16rem;
  left: -12rem;
  width: 36rem;
  height: 36rem;
  background: radial-gradient(circle, rgb(30 64 175 / 0.18), transparent 70%);
}
</style>
