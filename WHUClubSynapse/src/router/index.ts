import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/components/Layout/AppLayout.vue'
import HomeView from '@/views/User/HomeView.vue'
import { useAuthStore } from '@/stores/auth'
import { nextTick } from 'vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to, from, savedPosition) {
    // 如果有保存的位置（比如浏览器后退），则恢复到保存的位置
    if (savedPosition) {
      return savedPosition
    }
    // 否则滚动到顶部
    return { top: 0 }
  },
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
          component: () => import('@/views/User/ClubDetailView.vue'),
        },
        {
          path: '/club/:clubId/post/:postId',
          name: 'club-post-detail',
          component: () => import('@/views/User/ClubPostDetailView.vue'),
        },
        {
          path: '/search',
          name: 'search',
          component: () => import('@/views/User/SearchView.vue'),
        },
        {
          path: '/user',
          name: 'user',
          component: () => import('@/views/User/UserView.vue'),
          meta: { requiresAuth: true },
          children: [
            {
              path: '/user/center',
              name: 'user-center',
              component: () => import('@/views/User/UserCenterView.vue'),
              meta: { requiresAuth: true },
            },
            {
              path: '/user/applications',
              name: 'user-applications',
              component: () => import('@/views/User/MyApplicationsView.vue'),
              meta: { requiresAuth: true },
            },
            {
              path: '/user/favorites',
              name: 'user-favorites',
              component: () => import('@/views/User/MyFavoritesView.vue'),
              meta: { requiresAuth: true },
            },
            {
              path: '/user/clubs/joined',
              name: 'user-clubs-joined',
              component: () => import('@/views/User/JoinedClubs.vue'),
              meta: { requiresAuth: true },
            },
            {
              path: '/user/clubs/managed',
              name: 'user-clubs-managed',
              component: () => import('@/views/User/ManagedClubs.vue'),
              meta: { requiresAuth: true },
            },
            {
              path: '/user/edit-club/:id',
              name: 'EditClub',
              component: () => import('@/views/User/EditClubView.vue'),
              meta: { requiresAuth: true },
            },
            {
              path: '/user/club/:id/members',
              name: 'ClubMemberManagement',
              component: () => import('@/views/User/ClubMemberManagementView.vue'),
              meta: { requiresAuth: true },
            },
            {
              path: '/user/clubs',
              name: 'user-clubs',
              redirect:'/user/clubs/joined',
              meta: { requiresAuth: true },
            }, 
            
          ],
        },
      ],
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/Login/RegisterView.vue'),
    },
    {
      path: '/test',
      name: 'test',
      component: () => import('@/views/test.vue'),
    },
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 检查是否需要认证
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    // 未登录用户访问需要认证的页面，重定向到登录页
    next({
      path: '/login',
      query: { redirect: to.fullPath },
    })
  } else {
    next()
  }
})

// 添加路由后置守卫来强制滚动到顶部
router.afterEach((to, from) => {
  // 使用 nextTick 确保 DOM 更新完成后再滚动
  nextTick(() => {
    // 尝试多种滚动方式
    window.scrollTo({ top: 0, behavior: 'smooth' })
    document.documentElement.scrollTop = 0
    document.body.scrollTop = 0
    
    // 如果页面有特殊的滚动容器，也尝试滚动它们
    const mainElement = document.querySelector('.app-main')
    if (mainElement) {
      mainElement.scrollTop = 0
    }
    
    const containerElement = document.querySelector('.app-container')
    if (containerElement) {
      containerElement.scrollTop = 0
    }
  })
})

export default router
