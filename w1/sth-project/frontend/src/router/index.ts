import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/tickets'
  },
  {
    path: '/tickets',
    name: 'Tickets',
    component: () => import('@/views/TicketsPage.vue'),
    meta: {
      title: 'Ticket 管理'
    }
  },
  {
    path: '/tags',
    name: 'Tags',
    component: () => import('@/views/TagsPage.vue'),
    meta: {
      title: '标签管理'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || 'Ticket 标签管理'} - Ticket Manager`
  next()
})

export default router
