<script setup>
defineProps({ name: { type: String, required: true } })

const PATHS = {
  office: 'M3 21h18M5 21V7l7-4 7 4v14M9 21v-6h6v6',
  budget: 'M12 3v18M17 7H9.5a3 3 0 000 6h5a3 3 0 010 6H6',
  gantt: 'M4 5h8M8 10h10M6 15h7M11 20h9',
  team: 'M16 19v-1a4 4 0 00-4-4H7a4 4 0 00-4 4v1M9.5 10a3 3 0 100-6 3 3 0 000 6M21 19v-1a4 4 0 00-3-3.9M16 4.1a3 3 0 010 5.8',
  network: 'M5 6a2 2 0 100-4 2 2 0 000 4zM19 13a2 2 0 100-4 2 2 0 000 4zM5 22a2 2 0 100-4 2 2 0 000 4zM6.7 5l10.6 5M6.7 19l10.6-6',
  reports: 'M4 20V10M10 20V4M16 20v-7M22 20H2',
  calendar: 'M4 5h16v16H4zM4 10h16M9 3v4M15 3v4',
  control: 'M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0M16 4v4M10 10v4M18 16v4',
  help: 'M12 22a10 10 0 100-20 10 10 0 000 20zM9.1 9a3 3 0 015.8 1c0 2-3 3-3 3M12 17h.01',
  mail: 'M3 5h18v14H3zM3 6l9 7 9-7',
  phone: 'M22 16.9v3a2 2 0 01-2.2 2 19.8 19.8 0 01-8.6-3.1 19.5 19.5 0 01-6-6A19.8 19.8 0 012.1 4.2 2 2 0 014.1 2h3a2 2 0 012 1.7c.1 1 .4 1.9.7 2.8a2 2 0 01-.5 2.1L8 9.9a16 16 0 006 6l1.3-1.3a2 2 0 012.1-.4c.9.3 1.8.6 2.8.7a2 2 0 011.7 2z',
  meeting: 'M17 20v-2a4 4 0 00-4-4H7a4 4 0 00-4 4v2M10 10a4 4 0 100-8 4 4 0 000 8',
  play: 'M7 4l12 8-12 8z',
  pause: 'M7 4h3v16H7zM14 4h3v16h-3z',
  close: 'M6 6l12 12M18 6L6 18',
  clock: 'M12 22a10 10 0 100-20 10 10 0 000 20zM12 6v6l4 2',
}
</script>

<template>
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path :d="PATHS[name]" />
  </svg>
</template>
