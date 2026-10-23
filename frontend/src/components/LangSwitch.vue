<script setup>
import { useI18n } from 'vue-i18n'
import { setLocale } from '../i18n/index.js'

defineProps({ disabled: Boolean })
const { locale } = useI18n()
</script>

<template>
  <div class="inline-flex rounded-lg border border-slate-200 bg-white p-0.5 text-xs font-medium">
    <button
      v-for="l in ['en', 'ru']"
      :key="l"
      :disabled="disabled"
      class="rounded-md px-2.5 py-1 uppercase transition disabled:cursor-not-allowed"
      :class="locale === l ? 'bg-slate-900 text-white' : 'text-slate-500 hover:text-slate-900'"
      @click="setLocale(l)"
    >
      {{ l }}
    </button>
  </div>
</template>
