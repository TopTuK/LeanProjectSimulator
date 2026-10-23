<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { GUIDE } from '../i18n/guide.js'

const { locale } = useI18n()
const guide = computed(() => GUIDE[locale.value] ?? GUIDE.en)
</script>

<template>
  <div class="mx-auto max-w-3xl space-y-4">
    <div class="card p-6">
      <h2 class="text-lg font-semibold text-slate-900">{{ guide.title }}</h2>
      <p class="mt-2 text-sm leading-relaxed text-slate-600">{{ guide.intro }}</p>
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
