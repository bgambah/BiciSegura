<template>
  <div class="page">
    <h1>Elige tu ruta</h1>
    <p class="muted">Compara las opciones y decide cómo pedalear.</p>
    <p v-if="err" class="err">{{ err }} <router-link to="/">Volver a buscar</router-link></p>
    <div class="split">
      <div>
        <button v-for="(r, i) in routes" :key="r.id" class="card rcard" :class="{ on: i === cur }" @click="pick(i)">
          <b>{{ KINDS[r.p.kind] || r.p.kind }}</b>
          <span v-if="i === 0" class="tag">Tu preferencia</span>
          <div class="stats">
            <span><b>{{ minText(r.p.duration_s) }}</b><span class="muted">tiempo</span></span>
            <span><b>{{ kmText(r.p.distance_m) }}</b><span class="muted">distancia</span></span>
            <span><b :class="tone(r.p.safety_index)">{{ r.p.safety_index }}/100</b><span class="muted">seguridad</span></span>
          </div>
          <span class="muted">{{ r.p.bikeway_pct }}% por ciclorruta</span>
        </button>
        <p v-if="startErr" class="err">{{ startErr }}</p>
        <button class="btn" :disabled="!routes.length || busy" @click="start">{{ busy ? 'Iniciando…' : 'Iniciar recorrido' }}</button>
        <router-link to="/" class="btn ghost">Cambiar origen o destino</router-link>
      </div>
      <div ref="el" class="map"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createMap, dot, L } from '../lib/map'
import { api, errMsg, KINDS, kmText, minText, tone } from '../lib/api'

const route = useRoute(), router = useRouter()
const el = ref(null), routes = ref([]), cur = ref(0)
const err = ref(''), startErr = ref(''), busy = ref(false)
let map, lines = []
const COLORS = { safest: '#34d399', fastest: '#fbbf24', bikeways: '#a78bfa' }

const toLatLng = (coords) => coords.map(([lng, lat]) => [lat, lng])

function draw() {
  lines.forEach((l) => l.remove()); lines = []
  routes.value.forEach((r, i) => {
    const sel = i === cur.value
    const line = L.polyline(toLatLng(r.geometry.coordinates), {
      color: COLORS[r.p.kind] || '#8b5cf6', weight: sel ? 7 : 4, opacity: sel ? 1 : 0.45
    }).addTo(map)
    line.on('click', () => pick(i))
    if (sel) line.bringToFront()
    lines.push(line)
  })
}

function pick(i) {
  cur.value = i
  draw()
  map.fitBounds(lines[i].getBounds(), { padding: [30, 30] })
}

async function start() {
  busy.value = true; startErr.value = ''
  try {
    const { data } = await api.post('/trips/', { route: routes.value[cur.value].id })
    router.push(`/recorrido/${data.id}`)
  } catch (e) {
    startErr.value = errMsg(e)
  } finally {
    busy.value = false
  }
}

onMounted(async () => {
  map = createMap(el.value)
  const ids = String(route.query.ids || '').split(',').filter(Boolean)
  if (!ids.length) { err.value = 'No hay rutas para mostrar.'; return }
  try {
    const res = await Promise.all(ids.map((id) => api.get(`/routes/${id}/`)))
    routes.value = res.map(({ data }, i) => ({ id: ids[i], geometry: data.geometry, p: data.properties }))
  } catch (e) { err.value = errMsg(e); return }
  const c = routes.value[0].geometry.coordinates
  const [a, b] = [c[0], c[c.length - 1]]
  dot(map, [a[1], a[0]], '#34d399'); dot(map, [b[1], b[0]], '#8b5cf6')
  pick(0)
})
onBeforeUnmount(() => map?.remove())
</script>
