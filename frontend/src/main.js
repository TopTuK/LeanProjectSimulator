import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router.js'
import i18n from './i18n/index.js'
import './style.css'

createApp(App).use(createPinia()).use(router).use(i18n).mount('#app')
