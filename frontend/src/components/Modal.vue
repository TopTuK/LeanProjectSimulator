<script setup>
import { onBeforeUnmount, onMounted } from 'vue'
import Icon from './Icon.vue'

defineProps({ title: String, wide: Boolean })
const emit = defineEmits(['close'])

const onKey = (e) => e.key === 'Escape' && emit('close')
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
</script>

<template>
  <div class="fixed inset-0 z-40 flex items-end justify-center bg-slate-900/30 p-4 sm:items-center" @mousedown.self="emit('close')">
    <div class="card flex max-h-[90vh] w-full flex-col shadow-xl" :class="wide ? 'max-w-3xl' : 'max-w-xl'">
      <div class="flex items-start justify-between gap-4 border-b border-slate-100 px-6 py-4">
        <div class="min-w-0">
          <slot name="header"><h2 class="text-base font-semibold text-slate-900">{{ title }}</h2></slot>
        </div>
        <button class="-mr-2 rounded-lg p-1.5 text-slate-400 hover:bg-slate-50 hover:text-slate-700" @click="emit('close')">
          <Icon name="close" class="h-5 w-5" />
        </button>
      </div>
      <div class="overflow-y-auto px-6 py-5">
        <slot />
      </div>
      <div v-if="$slots.footer" class="flex flex-wrap justify-end gap-2 border-t border-slate-100 px-6 py-4">
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>
