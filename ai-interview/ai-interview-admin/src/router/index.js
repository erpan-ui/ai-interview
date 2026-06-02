import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { auth: true } },
  { path: '/users', name: 'Users', component: () => import('../views/Users.vue'), meta: { auth: true } },
  { path: '/interviews', name: 'Interviews', component: () => import('../views/Interviews.vue'), meta: { auth: true } },
  { path: '/interviews/:id', name: 'InterviewDetail', component: () => import('../views/InterviewDetail.vue'), meta: { auth: true } }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.auth && !authStore.isLoggedIn) next('/login')
  else next()
})

export default router
