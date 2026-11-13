<template>
  <div class="page">
    <h1>Cuidémonos en la vía</h1>
    <p class="muted">Tu reporte ayuda a otros biciusuarios.</p>
    <div class="split">
      <div>
        <label>1 · ¿Qué ocurrió?</label>
        <div class="grid">
          <button v-for="t in TYPES" :key="t.v" class="opt" :class="{ on: form.type === t.v }" @click="form.type = t.v">
            <img :src="t.icon" alt="" width="24" height="31" />{{ t.l }}
          </button>
        </div>
        <label>2 · Severidad</label>
        <div class="grid">
          <button v-for="(l, v) in SEVERITY" :key="v" class="opt" :class="{ on: form.severity === v }" @click="form.severity = v">{{ l }}</button>
        </div>
      </div>
      <div>
        <label>3 · Ubicación</label>
        <div ref="el" class="map" style="margin-top:0"></div>
        <p class="muted">{{ pos ? 'Ubicación marcada.' : 'Toca el mapa para marcar dónde ocurrió.' }}</p>
        <button class="btn ghost" @click="locate">Usar mi ubicación</button>
        <label>Descripción</label>
        <textarea v-model="form.description" rows="3" placeholder="Cuenta qué ocurrió"></textarea>
        <p v-if="err" class="err">{{ err }}</p>
        <button class="btn" :disabled="!pos" @click="send">Enviar reporte</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { TYPES, SEVERITY, iconFor, createMap, L } from '../lib/map'
import { api, errMsg } from '../lib/api'

const router = useRouter()
const el = ref(null), pos = ref(null), err = ref('')
const form = ref({ type: 'theft', severity: 'medium', description: '' })
let map, marker

function place(lat, lng) {
  pos.value = { lat, lng }
  if (marker) marker.setLatLng([lat, lng])
  else marker = L.marker([lat, lng], { icon: iconFor(form.value.type) }).addTo(map)
}
function locate() {
  navigator.geolocation?.getCurrentPosition(
    (p) => { place(p.coords.latitude, p.coords.longitude); map.setView([p.coords.latitude, p.coords.longitude], 15) },
    () => (err.value = 'No pudimos obtener tu ubicación. Márcala en el mapa.')
  )
}
async function send() {
  err.value = ''
  try {
    await api.post('/reports/', {
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [pos.value.lng, pos.value.lat] },
      properties: { ...form.value }
    })
    router.push('/incidentes')
  } catch (e) {
    if (e.response?.status === 401) return router.push('/login') // sesión vencida
    err.value = errMsg(e)
  }
}
watch(() => form.value.type, (t) => marker?.setIcon(iconFor(t)))
onMounted(() => { map = createMap(el.value); map.on('click', (e) => place(e.latlng.lat, e.latlng.lng)) })
</script>

<style scoped>
@media(min-width:900px){.map{height:360px}}
</style>
