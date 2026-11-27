<script setup>
import { useI18n } from 'vue-i18n'
import { useAuth } from '../stores/auth.js'
import yandexIcon from '../assets/login/login-icon-yandex.jpg'
import vkIcon from '../assets/login/login-icon-vk.jpg'
import okIcon from '../assets/login/login-icon-ok.jpg'
import mailIcon from '../assets/login/login-icon-mail.jpg'
import googleIcon from '../assets/login/login-icon-google.jpg'

defineProps({ next: { type: String, default: '/simulations' } })
const { t } = useI18n()
const auth = useAuth()

const PROVIDERS = [
  { id: 'yandex', icon: yandexIcon },
  { id: 'vk', icon: vkIcon },
  { id: 'ok', icon: okIcon },
  { id: 'mail', icon: mailIcon },
  { id: 'google', icon: googleIcon },
]
</script>

<template>
  <div class="grid gap-3" data-test="login-options">
    <button
      v-for="p in PROVIDERS"
      :key="p.id"
      class="group flex w-full items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 text-left text-sm font-medium text-slate-700 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2"
      :data-test="`login-${p.id}`"
      @click="auth.login(p.id, next)"
    >
      <span class="grid h-9 w-9 shrink-0 place-items-center overflow-hidden rounded-lg border border-slate-100">
        <img :src="p.icon" :alt="t(`auth.providers.${p.id}`)" class="h-full w-full object-cover" />
      </span>
      <span>{{ t('auth.continueWith', { provider: t(`auth.providers.${p.id}`) }) }}</span>
      <svg viewBox="0 0 20 20" class="ml-auto h-4 w-4 text-slate-300 transition group-hover:translate-x-0.5 group-hover:text-accent" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 10h11M11 5l5 5-5 5" /></svg>
    </button>
  </div>
</template>
