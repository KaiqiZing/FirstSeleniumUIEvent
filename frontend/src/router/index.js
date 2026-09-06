import { createRouter, createWebHistory } from 'vue-router'
import { scenarios, routeOf } from '../data/scenarios'

const viewModules = import.meta.glob('../views/**/*.vue')

function loadView(s) {
  const mod = viewModules[`../views/${s.group}/${s.file}.vue`]
  if (!mod) {
    console.error('缺少场景页面文件:', s.group, s.file)
    return () => import('../views/home/Home.vue')
  }
  return mod
}

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/home/Home.vue'),
    meta: { title: '场景总览' }
  }
]

for (const s of scenarios) {
  routes.push({
    path: routeOf(s),
    name: s.code,
    component: loadView(s),
    meta: { code: s.code, title: s.title, group: s.group }
  })
}

routes.push({ path: '/:pathMatch(.*)*', redirect: '/' })

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

export default router
