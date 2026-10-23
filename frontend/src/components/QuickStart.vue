<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { QUICK_START } from '../i18n/guide.js'

const props = defineProps({ helpTo: String })
const { locale } = useI18n()
const text = computed(() => QUICK_START[locale.value] ?? QUICK_START.en)

const KEY = 'simultrain:quickstart-hidden'
const hidden = ref(false)
try {
  hidden.value = localStorage.getItem(KEY) === '1'
} catch {}
function setHidden(v) {
  hidden.value = v
  try {
    localStorage.setItem(KEY, v ? '1' : '0')
  } catch {}
}
</script>

<template>
  <button v-if="hidden" class="text-sm text-accent hover:underline" @click="setHidden(false)">{{ text.title }}</button>
  <section v-else class="card p-5">
    <div class="flex items-start justify-between gap-4">
      <h2 class="font-medium text-slate-900">{{ text.title }}</h2>
      <div class="flex shrink-0 gap-4 text-sm">
        <RouterLink v-if="props.helpTo" :to="props.helpTo" class="text-accent hover:underline">{{ text.more }} →</RouterLink>
        <button class="text-slate-400 hover:text-slate-700" @click="setHidden(true)">{{ text.hide }}</button>
      </div>
    </div>
    <ol class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
      <li v-for="(step, i) in text.steps" :key="i" class="flex gap-3 text-sm leading-relaxed text-slate-600 lg:flex-col lg:gap-2">
        <span class="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-accent-soft text-xs font-semibold text-accent">{{ i + 1 }}</span>
        <span>{{ step }}</span>
      </li>
    </ol>
  </section>
</template>
