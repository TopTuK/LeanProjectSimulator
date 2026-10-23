import { useI18n } from 'vue-i18n'

export function useFormat() {
  const { t, locale } = useI18n()

  const money = (n) =>
    new Intl.NumberFormat(locale.value, { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(n ?? 0)
  const num = (n, digits = 0) =>
    new Intl.NumberFormat(locale.value, { maximumFractionDigits: digits, minimumFractionDigits: digits }).format(n ?? 0)
  const pct = (n) => `${num(n, 0)}%`
  const hhmm = (c) => `${c.hour}:${String(c.minute ?? 0).padStart(2, '0')}`
  const clockLabel = (c) => `${hhmm(c)} | ${t(`weekdays.${c.weekday}`)} | ${t('weekN', { n: c.week })}`
  const shortTime = (c) => `${t(`weekdaysShort.${c.weekday}`)} ${hhmm(c)}`

  return { money, num, pct, hhmm, clockLabel, shortTime }
}

/** Colour band for a 0-120 index. */
export function indexTone(v) {
  if (v >= 97) return 'good'
  if (v >= 90) return 'warn'
  return 'bad'
}
