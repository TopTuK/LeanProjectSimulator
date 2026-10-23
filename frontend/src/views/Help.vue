<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { GUIDE } from '../i18n/guide.js'
import guideImg from '../assets/guide.jpg'

const { locale } = useI18n()
const guide = computed(() => GUIDE[locale.value] ?? GUIDE.en)
</script>

<template>
  <div class="mx-auto max-w-3xl space-y-4">
    <div class="card p-6">
      <div class="flex items-center gap-6">
        <div class="min-w-0">
          <h2 class="text-lg font-semibold text-slate-900">{{ guide.title }}</h2>
          <p class="mt-2 text-sm leading-relaxed text-slate-600">{{ guide.intro }}</p>
        </div>
        <img :src="guideImg" alt="" class="hidden h-28 w-auto shrink-0 mix-blend-multiply sm:block" />
      </div>
    </div>
    <section v-for="s in guide.sections" :key="s.title" class="card p-6">
      <h3 class="font-medium text-slate-900">{{ s.title }}</h3>
      <ul class="mt-3 space-y-2 text-sm leading-relaxed text-slate-700">
        <li v-for="(item, i) in s.items" :key="i" class="flex gap-3">
          <span class="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
          <span>{{ item }}</span>
        </li>
      </ul>
    </section>
  </div>
</template>
