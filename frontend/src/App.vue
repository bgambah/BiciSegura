<template>
  <div class="shell" :class="{ bare: $route.meta.bare }">
    <aside v-if="!$route.meta.bare" class="side">
      <header class="top">
        <!-- Logo: reemplaza el archivo frontend/public/logo.svg por el tuyo -->
        <RouterLink to="/" class="logo"><img src="/logo.svg" alt="BiciSegura" /></RouterLink>
      </header>
      <nav class="tabs">
        <RouterLink v-for="t in tabs" :key="t.to" :to="t.to" :class="{ on: active(t) }"><span>{{ t.i }}</span>{{ t.l }}</RouterLink>
      </nav>
    </aside>
    <router-view />
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
// m: otras rutas que también marcan la pestaña como activa
const tabs = [
  { to: '/', i: '🧭', l: 'Rutas', m: ['/elegir', '/recorrido'] },
  { to: '/incidentes', i: '📍', l: 'Incidentes' },
  { to: '/reportar', i: '➕', l: 'Reportar' },
  { to: '/perfil', i: '👤', l: 'Perfil' }
]
const active = (t) => route.path === t.to || (t.m || []).some((p) => route.path.startsWith(p))
</script>

<style scoped>
.shell{min-height:100vh}
.side{display:contents}
.top{display:flex;align-items:center;padding:.7rem 1rem;border-bottom:1px solid var(--line)}
.logo{display:block;line-height:0}
.logo img{display:block;height:40px;width:auto;max-width:100%}
.tabs{position:fixed;bottom:0;left:0;right:0;display:flex;background:var(--bg);border-top:1px solid var(--line);padding-bottom:env(safe-area-inset-bottom);z-index:1000}
.tabs a{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;padding:.6rem 0;font-size:.75rem;color:var(--mut);text-decoration:none}
.tabs a.on{color:var(--acc)}

/* PC: la barra inferior pasa a ser un menú lateral */
@media(min-width:900px){
  .shell:not(.bare){display:grid;grid-template-columns:240px 1fr}
  .side{display:flex;flex-direction:column;position:sticky;top:0;height:100vh;border-right:1px solid var(--line);padding:1rem}
  .top{border:0;padding:0 0 1.5rem}
  .logo img{height:48px;max-width:100%}
  .tabs{position:static;flex-direction:column;gap:.3rem;border:0;padding:0}
  .tabs a{flex:none;flex-direction:row;justify-content:flex-start;gap:.7rem;padding:.7rem .8rem;font-size:.95rem;border-radius:10px}
  .tabs a.on{background:var(--sel)}
}
</style>
