<template>
  <div class="page">
    <h1>¿A dónde pedaleamos?</h1>
    <p class="muted">Encuentra una ruta más segura por Bogotá.</p>
    <div class="split">
      <div class="card">
        <label>Origen</label>
        <input v-model="origen" placeholder="Escribe una dirección o toca el mapa" @focus="target = 'o'" @input="edit('o')" />
        <button type="button" class="btn ghost sm" @click="locate">Usar mi ubicación</button>
        <label>Destino</label>
        <input v-model="destino" placeholder="Parque de la 93, Bogotá" @focus="target = 'd'" @input="edit('d')" />
        <label>Preferencia de ruta</label>
        <div class="seg">
          <button v-for="(l, k) in KINDS" :key="k" type="button" :class="{ on: pref === k }" @click="pref = k">{{ l }}</button>
        </div>
        <p v-if="err" class="err">{{ err }}</p>
        <button class="btn" :disabled="busy" @click="search">{{ busy ? 'Buscando…' : 'Buscar rutas' }}</button>
        <p class="muted">Toca el mapa para marcar el {{ target === 'o' ? 'origen' : 'destino' }}.</p>
      </div>
      <div ref="el" class="map"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { createMap, dot } from '../lib/map'
import { api, errMsg, KINDS } from '../lib/api'

const router = useRouter()
const el = ref(null)
const origen = ref(''), destino = ref(''), pref = ref('safest')
const pO = ref(null), pD = ref(null)   // coordenadas {lat, lng} de cada punto
const target = ref('o')                // qué punto marca el próximo toque en el mapa
const busy = ref(false), err = ref('')
let map
const pins = {}

function setPoint(which, lat, lng, text) {
  const color = which === 'o' ? '#34d399' : '#8b5cf6'
  if (which === 'o') { pO.value = { lat, lng }; origen.value = text } else { pD.value = { lat, lng }; destino.value = text }
  if (pins[which]) pins[which].setLatLng([lat, lng])
  else pins[which] = dot(map, [lat, lng], color)
}

// Si la persona vuelve a escribir, el punto anterior deja de valer
function edit(which) {
  if (which === 'o') pO.value = null; else pD.value = null
  pins[which]?.remove(); delete pins[which]
}

function locate() {
  err.value = ''
  if (!navigator.geolocation) { err.value = 'Tu navegador no permite obtener la ubicación. Márcala en el mapa.'; return }
  navigator.geolocation.getCurrentPosition(
    (p) => {
      setPoint('o', p.coords.latitude, p.coords.longitude, 'Mi ubicación actual')
      map.setView([p.coords.latitude, p.coords.longitude], 14)
      target.value = 'd'
    },
    () => (err.value = 'No pudimos obtener tu ubicación. Márcala en el mapa.')
  )
}

// Convierte una dirección en coordenadas con Nominatim (OpenStreetMap), limitado a Bogotá
async function geocode(q) {
  const url = 'https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&countrycodes=co&bounded=1' +
    '&viewbox=-74.25,4.85,-73.99,4.45&q=' + encodeURIComponent(q)
  const d = await (await fetch(url)).json()
  return d[0] ? { lat: +d[0].lat, lng: +d[0].lon } : null
}

async function search() {
  err.value = ''; busy.value = true
  try {
    for (const w of ['o', 'd']) {
      if ((w === 'o' ? pO : pD).value) continue
      const txt = (w === 'o' ? origen : destino).value.trim()
      if (!txt) { err.value = `Marca el ${w === 'o' ? 'origen' : 'destino'} en el mapa o escribe una dirección.`; return }
      const g = await geocode(txt)
      if (!g) { err.value = `No encontramos "${txt}" en Bogotá. Prueba con otra dirección o márcala en el mapa.`; return }
      setPoint(w, g.lat, g.lng, txt)
    }
    const { data } = await api.post('/routes/search/', { origin: pO.value, destination: pD.value, preference: pref.value })
    const ids = (data.features || data).map((f) => f.id ?? f.properties?.id)
    router.push({ path: '/elegir', query: { ids: ids.join(',') } })
  } catch (e) {
    err.value = errMsg(e)
  } finally {
    busy.value = false
  }
}

onMounted(() => {
  map = createMap(el.value)
  map.on('click', (e) => {
    setPoint(target.value, e.latlng.lat, e.latlng.lng, 'Punto en el mapa')
    if (target.value === 'o') target.value = 'd'
  })
})
onBeforeUnmount(() => map?.remove())
</script>
