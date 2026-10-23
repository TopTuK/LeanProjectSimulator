import { createI18n } from 'vue-i18n'
import en from './en.js'
import ru from './ru.js'

const KEY = 'simultrain:locale'

function initialLocale() {
  try {
    const saved = localStorage.getItem(KEY)
    if (saved === 'en' || saved === 'ru') return saved
  } catch {}
  return navigator.language?.startsWith('ru') ? 'ru' : 'en'
}

const i18n = createI18n({
  legacy: false,
  locale: initialLocale(),
  fallbackLocale: 'en',
  messages: { en, ru },
})

export function setLocale(locale) {
  i18n.global.locale.value = locale
  document.documentElement.lang = locale
  try {
    localStorage.setItem(KEY, locale)
  } catch {}
}

export default i18n
