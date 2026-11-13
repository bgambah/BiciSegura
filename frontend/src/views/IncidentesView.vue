<template>
  <div class="page">
    <h1>Pedalea con información</h1>
    <p class="muted">Incidentes y zonas de riesgo para biciusuarios.</p>
    <div class="seg">
      <button v-for="(l, k) in TABS" :key="k" :class="{ on: tab === k }" @click="setTab(k)">{{ l }}</button>
    </div>
    <div v-if="tab === 'inc'" class="row">
      <select v-model="tipo" @change="loadReports">
        <option value="">Todos los tipos</option>
        <option v-for="t in TYPES" :key="t.v" :value="t.v">{{ t.l }}</option>
      </select>
      <select v-model="dias" @change="loadReports">
        <option value="">Cualquier fecha</option>
        <option value="1">Hoy</option>
        <option value="7">Últimos 7 días</option>
        <option value="30">Últimos 30 días</option>
      </select>
    </div>
    <div class="split rev">
      <div ref="el" class="map"></div>
      <div>
        <p v-if="msg" class="muted">{{ msg }}</p>
        <template v-if="tab === 'inc'">
          <div v-if="sel" class="card">
            <b>{{ label(sel.type) }}</b> <span class="sev">Severidad {{ SEVERITY[sel.severity]?.toLowerCase() }}</span>
            <p>{{ sel.description || 'Sin descripción' }}</p>
            <p class="muted">Reportado {{ new Date(sel.created_at).toLocaleString('es-CO') }}</p>
            <div class="row">
              <button class="btn ghost sm" :disabled="!logged || busy" @click="vote('confirm')">Sigue ocurriendo ({{ sel.confirmation_count }})</button>
              <button class="btn ghost sm" :disabled="!logged || busy" @click="vote('solve')">Ya se solucionó ({{ sel.solved_count }})</button>
            </div>
            <p v-if="!logged" class="muted">Inicia sesión para confirmar un incidente o marcarlo como solucionado.</p>
          </div>
          <p v-else class="muted">{{ count }} incidentes activos. Toca un marcador para ver el detalle.</p>
          <router-link to="/reportar" class="btn">Reportar un incidente</router-link>
        </template>
        <template v-else-if="tab === 'zonas'">
          <p class="muted">Las zonas en rojo son sectores con índice de seguridad bajo, calculado con los incidentes activos.</p>
          <p v-if="empty" class="muted">Por ahora no hay zonas inseguras. Cuando se acumulen reportes aparecerán aquí.</p>
        </template>
        <template v-else>
          <p class="muted">Los tramos en verde son ciclorrutas. Mueve el mapa para ver las de otra zona.</p>
          <p v-if="empty" class="muted">No hay ciclorrutas registradas en esta zona del mapa.</p>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { TYPES, SEVERITY, iconFor, createMap, L } from '../lib/map'
import { api, errMsg, hasToken } from '../lib/api'

const TABS = { inc: 'Incidentes', zonas: 'Zonas inseguras', bici: 'Ciclorrutas' }
const el = ref(null), tab = ref('inc'), tipo = ref(''), dias = ref('')
const sel = ref(null), count = ref(0), busy = ref(false), msg = ref(''), empty = ref(false)
const logged = hasToken()   // confirmar y solucionar exigen sesión
let map, layer, timer

const label = (v) => TYPES.find((t) => t.v === v)?.l || v

function clear() {
  if (layer) { map.removeLayer(layer); layer = null }
  sel.value = null; msg.value = ''; empty.value = false
}

async function loadReports() {
  const t = tab.value
  clear()
  try {
    const { data } = await api.get('/reports/', { params: { type: tipo.value || undefined, days: dias.value || undefined } })
    if (tab.value !== t) return   // la persona cambió de pestaña mientras cargaba
    const feats = data.features || []
    count.value = feats.length
    layer = L.geoJSON(feats, {
      pointToLayer: (f, ll) => L.marker(ll, { icon: iconFor(f.properties.type) }),
      onEachFeature: (f, l) => l.on('click', () => {
        f.properties.id = f.id ?? f.properties.id
        sel.value = f.properties
        msg.value = ''
      })
    }).addTo(map)
  } catch (e) { msg.value = errMsg(e) }
}

async function vote(kind) {
  busy.value = true; msg.value = ''
  try {
    const { data } = await api.post(`/reports/${sel.value.id}/${kind}/`)
    if (data.properties.state !== 'active') {
      await loadReports()   // el incidente se resolvió: sale del mapa
      msg.value = 'Con tu voto el incidente quedó como solucionado.'
    } else {
      Object.assign(sel.value, data.properties)
      msg.value = kind === 'confirm' ? 'Gracias, registramos que sigue ocurriendo.' : 'Gracias, registramos tu voto.'
    }
  } catch (e) {
    msg.value = errMsg(e)   // por ejemplo, si ya votaste
  } finally {
    busy.value = false
  }
}

async function loadZones() {
  const t = tab.value
  clear()
  try {
    const { data } = await api.get('/zones/unsafe/', { params: { threshold: 60 } })
    if (tab.value !== t) return
    const feats = data.features || []
    empty.value = !feats.length
    layer = L.geoJSON(feats, {
      style: { color: '#f87171', weight: 1, fillColor: '#f87171', fillOpacity: 0.35 },
      onEachFeature: (f, l) => {
        const i = f.properties?.safety_index ?? f.properties?.index
        l.bindPopup(Number.isFinite(+i) && i !== null ? `Índice de seguridad: ${Math.round(+i)}` : 'Zona con índice de seguridad bajo')
      }
    }).addTo(map)
  } catch (e) { msg.value = errMsg(e) }
}

async function loadBikeways() {
  const t = tab.value
  clear()
  try {
    const { data } = await api.get('/bikeways/', { params: { bbox: map.getBounds().toBBoxString() } })
    if (tab.value !== t) return
    const feats = data.features || []
    empty.value = !feats.length
    layer = L.geoJSON(feats, {
      style: { color: '#34d399', weight: 4 },
      onEachFeature: (f, l) => {
        if (!f.properties?.name) return
        const d = document.createElement('div')
        d.textContent = f.properties.name
        l.bindPopup(d)
      }
    }).addTo(map)
  } catch (e) { msg.value = errMsg(e) }
}

function setTab(k) {
  tab.value = k
  if (k === 'inc') loadReports()
  else if (k === 'zonas') loadZones()
  else loadBikeways()
}

onMounted(() => {
  map = createMap(el.value)
  // En ciclorrutas se piden solo las del área visible
  map.on('moveend', () => {
    if (tab.value !== 'bici') return
    clearTimeout(timer)
    timer = setTimeout(loadBikeways, 400)
  })
  loadReports()
})
onBeforeUnmount(() => { clearTimeout(timer); map?.remove() })
</script>

<style scoped>
.sev{color:var(--bad);font-size:.8rem;margin-left:.5rem}
.row{margin-top:.2rem}
.row select{flex:1;min-width:140px}
</style>
