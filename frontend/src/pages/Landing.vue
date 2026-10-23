<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { lastSessionId } from '../stores/sim.js'
import { useAuth } from '../stores/auth.js'
import { QUICK_START } from '../i18n/guide.js'
import LangSwitch from '../components/LangSwitch.vue'
import heroImg from '../assets/landing-hero.jpg'

const { t, locale } = useI18n()
const route = useRoute()
const auth = useAuth()
const quick = computed(() => QUICK_START[locale.value] ?? QUICK_START.en)
const last = lastSessionId()
const authError = computed(() => route.query.auth_error !== undefined)

onMounted(() => auth.fetch())
</script>

<template>
  <div class="flex min-h-full flex-col">
    <header class="mx-auto flex w-full max-w-5xl items-center justify-between px-6 py-5">
      <div class="flex items-center gap-2 font-semibold">
        <span class="grid h-7 w-7 place-items-center rounded-lg bg-accent text-white">
          <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 16l4-5 3 2.5L18 7" /></svg>
        </span>
        {{ t('app.name') }}
      </div>
      <div class="flex items-center gap-3">
        <template v-if="auth.user">
          <img v-if="auth.user.avatar_url" :src="auth.user.avatar_url" alt="" class="h-7 w-7 rounded-full" />
          <span class="text-sm text-slate-600" data-test="user-name">{{ auth.user.name }}</span>
          <button class="text-sm text-slate-500 hover:text-slate-900" data-test="logout" @click="auth.logout()">
            {{ t('auth.logout') }}
          </button>
        </template>
        <button v-else-if="auth.loaded" class="btn btn-ghost px-3 py-1.5 text-sm" data-test="login" @click="auth.login('/')">
          {{ t('auth.login') }}
        </button>
        <LangSwitch />
      </div>
    </header>

    <main class="mx-auto flex w-full max-w-5xl flex-1 flex-col justify-center px-6 pb-24">
      <div class="grid items-center gap-10 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <div>
          <p class="label mb-4">{{ t('app.tagline') }}</p>
          <h1 class="max-w-2xl text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl">{{ t('landing.title') }}</h1>
          <p class="mt-5 max-w-2xl text-lg leading-relaxed text-slate-600">{{ t('landing.lead') }}</p>

          <p v-if="authError" class="mt-6 text-sm text-red-600" data-test="auth-error">{{ t('auth.error') }}</p>

          <div class="mt-10 flex flex-wrap items-center gap-3">
            <template v-if="auth.user">
              <RouterLink to="/control" class="btn btn-primary px-6 py-3 text-base" data-test="start">
                {{ t('landing.start') }}
                <svg viewBox="0 0 20 20" class="h-4 w-4" fill="currentColor"><path d="M7 4l7 6-7 6V4z" /></svg>
              </RouterLink>
              <RouterLink v-if="last" :to="`/sim/${last}`" class="btn btn-ghost px-5 py-3 text-base">
                {{ t('landing.resume') }}
              </RouterLink>
            </template>
            <button v-else class="btn btn-primary px-6 py-3 text-base" :disabled="!auth.loaded" data-test="login-start" @click="auth.login('/control')">
              {{ t('auth.loginToStart') }}
              <svg viewBox="0 0 20 20" class="h-4 w-4" fill="currentColor"><path d="M7 4l7 6-7 6V4z" /></svg>
            </button>
          </div>
        </div>

        <img :src="heroImg" alt="" class="hidden w-full max-w-md justify-self-center mix-blend-multiply lg:block" />
      </div>

      <h2 class="label mt-14">{{ quick.title }}</h2>
      <ol class="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <li v-for="(step, i) in quick.steps" :key="i" class="card flex flex-col gap-2 px-5 py-4 text-sm leading-relaxed text-slate-600">
          <span class="grid h-6 w-6 place-items-center rounded-full bg-accent-soft text-xs font-semibold text-accent">{{ i + 1 }}</span>
          {{ step }}
        </li>
      </ol>
      <p class="mt-6 text-sm text-slate-400">{{ t('landing.note') }}</p>
    </main>
  </div>
</template>
