<template>
  <div class="page">
    <h1>Tu perfil</h1>

    <div v-if="!logged" class="card" style="margin-top:1rem">
      <p>Estás en modo invitado. Inicia sesión para ver tu historial de recorridos y confirmar incidentes.</p>
      <router-link to="/login" class="btn">Iniciar sesión o registrarme</router-link>
    </div>

    <template v-else>
      <p v-if="err" class="err">{{ err }}</p>
      <div v-if="me" class="card" style="margin-top:1rem">
        <b>{{ me.full_name }}</b><span class="tag">{{ ROLE[me.role] || me.role }}</span>
        <p class="muted">{{ me.email }}</p>
        <div class="stats">
          <span><b>{{ me.reports_count }}</b><span class="muted">reportes</span></span>
          <span><b>{{ me.trips_count }}</b><span class="muted">recorridos</span></span>
          <span><b>{{ new Date(me.created_at).toLocaleDateString('es-CO') }}</b><span class="muted">miembro desde</span></span>
        </div>
      </div>

      <h2>Historial de recorridos</h2>
      <p v-if="loaded && !trips.length" class="muted">Aún no has hecho recorridos. Busca una ruta para empezar.</p>
      <p v-else-if="trips.length" class="muted">Toca un recorrido para verlo o cambiarle el nombre.</p>
      <router-link v-for="t in trips" :key="t.id" :to="`/recorrido/${t.id}`" class="card rcard">
        <b>{{ t.name || `Recorrido ${t.id}` }}</b><span class="tag">{{ STATUS[t.status] }}</span>
        <div class="muted">Inicio {{ new Date(t.started_at).toLocaleString('es-CO') }}</div>
        <div v-if="t.status !== 'active'" class="muted">Duración {{ clockText(t.elapsed_s) }}</div>
        <div v-if="t.finished_at" class="muted">Fin {{ new Date(t.finished_at).toLocaleString('es-CO') }}</div>
      </router-link>
      <router-link to="/login" class="btn ghost">Cerrar sesión</router-link>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api, errMsg, hasToken, STATUS, clockText } from '../lib/api'

const ROLE = { cyclist: 'Ciclista', administrator: 'Administrador' }
const logged = hasToken()
const me = ref(null), trips = ref([]), err = ref(''), loaded = ref(false)

onMounted(async () => {
  if (!logged) return
  try {
    const [m, t] = await Promise.all([api.get('/auth/me/'), api.get('/trips/')])
    me.value = m.data
    trips.value = t.data.results || t.data
  } catch (e) {
    err.value = errMsg(e)
  } finally {
    loaded.value = true
  }
})
</script>
