import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: () => import('../views/LoginView.vue'), meta: { bare: true } },
    { path: '/', component: () => import('../views/RutasView.vue') },
    { path: '/elegir', component: () => import('../views/ElegirRutaView.vue') },
    { path: '/recorrido/:id', component: () => import('../views/RecorridoView.vue') },
    { path: '/incidentes', component: () => import('../views/IncidentesView.vue') },
    { path: '/reportar', component: () => import('../views/ReportarView.vue') },
    { path: '/perfil', component: () => import('../views/PerfilView.vue') }
  ]
})

router.beforeEach((to) => {
  // Entrar a /login cierra la sesión (el perfil tiene el botón "Cerrar sesión")
  if (to.path === '/login') { localStorage.removeItem('token'); localStorage.removeItem('guest'); return true }
  // Sin sesión iniciada, todo lleva al inicio de sesión
  if (!localStorage.getItem('token') && !localStorage.getItem('guest')) return '/login'
})

export default router
