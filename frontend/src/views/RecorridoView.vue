<template>
  <div class="page">
    <h1>{{ TITLE[trip?.status] || 'Tu recorrido' }}</h1>
    <p v-if="err" class="err">{{ err }}</p>
    <div class="split">
      <div>
        <div v-if="trip" class="card">
          <div v-if="!editing" class="row namebar">
            <b class="tname">{{ trip.name || `Recorrido ${trip.id}` }}</b>
            <button type="button" class="btn ghost sm" @click="startEdit">Renombrar</button>
          </div>
          <div v-else>
            <input v-model="draft" maxlength="100" placeholder="Nombre del recorrido" aria-label="Nombre del recorrido"
                   @keyup.enter="saveName" @keyup.esc="editing = false" />
            <div class="row namebar">
              <button type="button" class="btn sm" :disabled="busy" @click="saveName">Guardar</button>
              <button type="button" class="btn ghost sm" @click="editing = false">Cancelar</button>
            </div>
            <p class="muted">Déjalo vacío para volver a "Recorrido {{ trip.id }}".</p>
          </div>

          <div class="clock" :class="{ off: trip.status !== 'active' }" role="timer" aria-live="off">{{ clock }}</div>
          <span class="muted">{{ CLOCK_LABEL[trip.status] }}</span>
        </div>

        <div v-if="info" class="card" style="margin-top:.6rem">
          <span class="tag" style="margin-left:0">{{ STATUS[trip.status] }}</span>
          <div class="stats">
            <span><b>{{ minText(info.duration_s) }}</b><span class="muted">tiempo estimado</span></span>
            <span><b>{{ kmText(info.distance_m) }}</b><span class="muted">distancia</span></span>
            <span><b :class="tone(info.safety_index)">{{ info.safety_index }}/100</b><span class="muted">seguridad</span></span>
          </div>
        </div>

        <template v-if="trip && trip.status !== 'finished'">
          <button v-if="trip.status === 'active'" class="btn ghost" :disabled="busy" @click="setStatus('paused')">Pausar</button>
          <button v-else class="btn" :disabled="busy" @click="setStatus('active')">Reanudar</button>
          <button class="btn" :disabled="busy" @click="setStatus('finished')">Finalizar recorrido</button>
        </template>
        <template v-else-if="trip">
          <router-link to="/" class="btn">Buscar otra ruta</router-link>
          <router-link to="/perfil" class="btn ghost">Ver mi historial</router-link>
        </template>

        <h2>Peligros cerca</h2>
        <p v-if="gps === false" class="muted">No tenemos tu ubicación. Mostramos los incidentes cerca del inicio de la ruta.</p>
        <p v-if="trip?.status !== 'active' && trip" class="muted">Los peligros se actualizan mientras el recorrido está en marcha.</p>
        <p v-else-if="!hazards.length" class="muted">No hay incidentes activos a menos de 300 m.</p>
        <div v-for="h in hazards" :key="h.id" class="card" style="margin-top:.6rem">
          <b>{{ h.label }}</b> <span class="muted">a {{ h.dist }} m</span>
          <div class="muted">Severidad {{ SEVERITY[h.severity]?.toLowerCase() }}</div>
        </div>
      </div>
      <div ref="el" class="map"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { createMap, dot, iconFor, L, TYPES, SEVERITY } from '../lib/map'
import { api, errMsg, STATUS, kmText, minText, tone, clockText } from '../lib/api'

const route = useRoute()
const el = ref(null), trip = ref(null), info = ref(null), hazards = ref([])
const err = ref(''), busy = ref(false)
const gps = ref(null)   // null: esperando, true: con GPS, false: sin GPS
const editing = ref(false), draft = ref('')
const TITLE = { active: 'Tu ruta está en marcha', paused: 'Recorrido en pausa', finished: 'Recorrido finalizado' }
const CLOCK_LABEL = { active: 'Tiempo de recorrido', paused: 'Cronómetro en pausa', finished: 'Tiempo total' }

// Cronómetro: el servidor manda los segundos acumulados (sin contar pausas) y aquí solo se
// avanza mientras el recorrido está en marcha. Así no depende del reloj del dispositivo.
const base = ref(0), now = ref(Date.now())
let t0 = Date.now(), tick
const clock = computed(() =>
  clockText(base.value + (trip.value?.status === 'active' ? Math.floor((now.value - t0) / 1000) : 0)))

function sync(data) {
  trip.value = data
  base.value = data.elapsed_s
  t0 = Date.now(); now.value = t0
}

function startEdit() { draft.value = trip.value.name; editing.value = true }

async function saveName() {
  busy.value = true; err.value = ''
  try {
    sync((await api.patch(`/trips/${trip.value.id}/`, { name: draft.value.trim() })).data)
    editing.value = false
  } catch (e) {
    err.value = errMsg(e)
  } finally {
    busy.value = false
  }
}

let map, watchId, pin, group, last = 0, here = null, startPt = null

async function loadHazards() {
  if (!here || trip.value?.status !== 'active') return
  last = Date.now()
  try {
    const { data } = await api.get('/reports/nearby/', { params: { lat: here.lat, lng: here.lng, radius: 300 } })
    const feats = data.features || []
    if (group) map.removeLayer(group)
    group = L.layerGroup(feats.map((f) => {
      const [lng, lat] = f.geometry.coordinates
      return L.marker([lat, lng], { icon: iconFor(f.properties.type) })
    })).addTo(map)
    const me = L.latLng(here.lat, here.lng)
    hazards.value = feats.map((f) => {
      const [lng, lat] = f.geometry.coordinates
      return {
        id: f.id ?? f.properties.id,
        label: TYPES.find((t) => t.v === f.properties.type)?.l || f.properties.type,
        severity: f.properties.severity,
        dist: Math.round(me.distanceTo([lat, lng]))
      }
    }).sort((a, b) => a.dist - b.dist).slice(0, 5)
  } catch (e) { console.error('Error cargando peligros cercanos:', e) }
}

function onPos(p) {
  gps.value = true
  here = { lat: p.coords.latitude, lng: p.coords.longitude }
  if (pin) pin.setLatLng([here.lat, here.lng]); else pin = dot(map, [here.lat, here.lng], '#60a5fa', 8)
  if (Date.now() - last > 15000) loadHazards()   // como máximo cada 15 s
}

// Sin GPS se usa el inicio de la ruta como referencia
function noGps() {
  gps.value = false
  if (!here) { here = startPt; loadHazards() }
}

function stopGps() {
  if (watchId != null) navigator.geolocation.clearWatch(watchId)
  watchId = null
}

async function setStatus(s) {
  busy.value = true; err.value = ''
  try {
    sync((await api.patch(`/trips/${trip.value.id}/`, { status: s })).data)
    if (s === 'finished') stopGps()
    else if (s === 'active') loadHazards()
  } catch (e) {
    err.value = errMsg(e)
  } finally {
    busy.value = false
  }
}

onMounted(async () => {
  map = createMap(el.value)
  tick = setInterval(() => { now.value = Date.now() }, 1000)
  try {
    sync((await api.get(`/trips/${route.params.id}/`)).data)
    const r = (await api.get(`/routes/${trip.value.route}/`)).data
    info.value = r.properties
    const ll = r.geometry.coordinates.map(([lng, lat]) => [lat, lng])
    const line = L.polyline(ll, { color: '#8b5cf6', weight: 6 }).addTo(map)
    map.fitBounds(line.getBounds(), { padding: [30, 30] })
    dot(map, ll[0], '#34d399'); dot(map, ll[ll.length - 1], '#a78bfa')
    startPt = { lat: ll[0][0], lng: ll[0][1] }
  } catch (e) { err.value = errMsg(e); return }
  if (trip.value.status === 'finished') return
  if (navigator.geolocation) watchId = navigator.geolocation.watchPosition(onPos, noGps, { enableHighAccuracy: true })
  else noGps()
})
onBeforeUnmount(() => { clearInterval(tick); stopGps(); map?.remove() })
</script>

<style scoped>
.namebar{justify-content:space-between;flex-wrap:nowrap}
.namebar .btn.sm{margin-top:0}
.tname{font-size:1.05rem;overflow-wrap:anywhere}
.clock{font:600 2.6rem/1.1 ui-monospace,Consolas,monospace;font-variant-numeric:tabular-nums;letter-spacing:.04em;margin:.9rem 0 .2rem}
.clock.off{color:var(--mut)}
</style>
