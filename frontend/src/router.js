import { createRouter, createWebHistory } from 'vue-router'
import Landing from './pages/Landing.vue'
import Control from './pages/Control.vue'
import Sim from './pages/Sim.vue'
import { useAuth } from './stores/auth.js'

export const VIEWS = ['office', 'help', 'budget', 'gantt', 'team', 'network', 'reports', 'calendar', 'control']

export const routes = [
  { path: '/', component: Landing },
  { path: '/control', component: Control, meta: { auth: true } },
  { path: '/sim/:id', redirect: (to) => `/sim/${to.params.id}/office` },
  { path: '/sim/:id/:view', component: Sim, props: true, meta: { auth: true } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export function createAppRouter(history = createWebHistory()) {
  const router = createRouter({ history, routes })
  router.beforeEach(async (to) => {
    if (!to.meta.auth) return true
    const auth = useAuth()
    if (await auth.fetch()) return true
    // the landing page opens the sign-in options and comes back here
    return { path: '/', query: { login: '1', next: to.fullPath } }
  })
  return router
}

export default createAppRouter()
