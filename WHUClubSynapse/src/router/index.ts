import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/components/Layout/AppLayout.vue'
import HomeView from '@/views/HomeView.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'home',
          component: HomeView,
        },
        {
          path: '/about',
          name: 'about',
          component: () => import('@/views/AboutView.vue'),
        },
        {
          path: '/club/:id',
          name: 'club-detail',
          component: () => import('@/views/ClubDetailView.vue'),
        },
        {
          path: '/search',
          name: 'search',
          component: () => import('@/views/SearchView.vue'),
        },
        {
          path: '/user/center',
          name: 'user-center',
          component: () => import('@/views/UserCenterView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: '/user/applications',
          name: 'user-applications',
          component: () => import('@/views/MyApplicationsView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: '/user/favorites',
          name: 'user-favorites',
          component: () => import('@/views/MyFavoritesView.vue'),
          meta: { requiresAuth: true },
        },
      ],
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
    },
  ],
})

// 路由守卫
// router.beforeEach((to, from, next) => {
//   const authStore = useAuthStore()

//   // 检查是否需要认证
//   if (to.meta.requiresAuth && !authStore.isLoggedIn) {
//     // 未登录用户访问需要认证的页面，重定向到登录页
//     next({
//       path: '/login',
//       query: { redirect: to.fullPath },
//     })
//   } else {
//     next()
//   }
// })

export default router
