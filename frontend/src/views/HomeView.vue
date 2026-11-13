<template>
  <div class="home">
    <h1>Mapa de Incidentes en Bogotá</h1>
    <p class="instruction">Haz clic en cualquier punto del mapa para reportar un incidente.</p>
    
    <div id="map"></div>

    <!-- Modal Flotante para el Formulario -->
    <div v-if="isReporting" class="modal-overlay">
      <div class="modal">
        <h2>Reportar Incidente</h2>
        <form @submit.prevent="submitReport">
          
          <label>Tipo de incidente:</label>
          <select v-model="reportForm.type" required>
            <option value="theft">Robo</option>
            <option value="accident">Accidente</option>
            <option value="pothole">Peligro en la vía / Hueco</option>
          </select>

          <label>Severidad:</label>
          <select v-model="reportForm.severity" required>
            <option value="low">Baja</option>
            <option value="medium">Media</option>
            <option value="high">Alta</option>
          </select>

          <label>Descripción detallada:</label>
          <textarea 
            v-model="reportForm.description" 
            rows="3" 
            placeholder="Ej: Dos sujetos me arrinconaron..."
            required
          ></textarea>

          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="isReporting = false">Cancelar</button>
            <button type="submit" class="btn-submit">Enviar Reporte</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import L from 'leaflet'
import axios from 'axios'
import 'leaflet/dist/leaflet.css'

import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png'
import iconUrl from 'leaflet/dist/images/marker-icon.png'
import shadowUrl from 'leaflet/dist/images/marker-shadow.png'

L.Icon.Default.mergeOptions({ iconRetinaUrl, iconUrl, shadowUrl })

// --- ÍCONOS PERSONALIZADOS POR TIPO DE INCIDENTE ---
// Para usar tus propias imágenes, reemplaza los archivos de src/assets/markers/
// (conservando el nombre) o cambia las rutas de import.
import theftImg from '../assets/markers/theft.svg'
import accidentImg from '../assets/markers/accident.svg'
import potholeImg from '../assets/markers/pothole.svg'
import defaultImg from '../assets/markers/default.svg'

const makeIcon = (url) =>
  L.icon({
    iconUrl: url,
    iconSize: [32, 42],     // tamaño de la imagen en píxeles
    iconAnchor: [16, 42],   // punta del pin: mitad del ancho, base de la imagen
    popupAnchor: [0, -38]   // el popup sale justo encima del pin
  })

const icons = {
  theft: makeIcon(theftImg),
  accident: makeIcon(accidentImg),
  pothole: makeIcon(potholeImg)
}
const defaultIcon = makeIcon(defaultImg)

// Etiquetas legibles para el popup
const typeLabels = { theft: 'Robo', accident: 'Accidente', pothole: 'Peligro / Hueco' }
const severityLabels = { low: 'Baja', medium: 'Media', high: 'Alta' }

const API_URL = 'http://127.0.0.1:8000/api/reports/'

// --- ESTADO DEL FORMULARIO ---
const isReporting = ref(false)
const reportForm = ref({
  lat: null,
  lng: null,
  type: 'theft',      // valores en minúscula: deben coincidir con el modelo de Django
  severity: 'high',
  description: ''
})

let map = null            // instancia del mapa
let incidentsLayer = null // capa con los incidentes (se reemplaza en cada recarga)

onMounted(async () => {
  map = L.map('map').setView([4.6097, -74.0817], 12)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
  }).addTo(map)

  // Cargar incidentes existentes
  loadIncidents()

  // --- EVENTO DE CLIC EN EL MAPA ---
  map.on('click', (e) => {
    // Al hacer clic, capturamos coordenadas y abrimos el modal
    reportForm.value.lat = e.latlng.lat
    reportForm.value.lng = e.latlng.lng
    isReporting.value = true
  })
})

const loadIncidents = async () => {
  try {
    const response = await axios.get(API_URL)
    const incidentes = response.data.features || []

    // Quitamos la capa anterior para no duplicar marcadores
    if (incidentsLayer) map.removeLayer(incidentsLayer)

    incidentsLayer = L.geoJSON(incidentes, {
      // Dibuja cada punto con el ícono que corresponde a su tipo
      pointToLayer: (feature, latlng) =>
        L.marker(latlng, { icon: icons[feature.properties.type] || defaultIcon }),
      onEachFeature: (feature, layer) => {
        const props = feature.properties

        // Usamos textContent para evitar inyección de HTML desde la descripción
        const div = document.createElement('div')
        div.innerHTML =
          '<strong>Tipo:</strong> <span class="p-type"></span><br>' +
          '<strong>Severidad:</strong> <span class="p-sev"></span>' +
          '<p class="p-desc"></p>'
        div.querySelector('.p-type').textContent = typeLabels[props.type] || props.type
        div.querySelector('.p-sev').textContent = severityLabels[props.severity] || props.severity
        div.querySelector('.p-desc').textContent = props.description || 'Sin descripción'

        layer.bindPopup(div)
      }
    }).addTo(map)
  } catch (error) {
    console.error('Error cargando incidentes:', error)
  }
}

// --- FUNCIÓN PARA ENVIAR EL NUEVO REPORTE ---
const submitReport = async () => {
  // GeoFeatureModelSerializer exige formato GeoJSON para crear el dato
  const payload = {
    type: 'Feature',
    geometry: {
      type: 'Point',
      coordinates: [reportForm.value.lng, reportForm.value.lat] // GeoJSON: [Longitud, Latitud]
    },
    properties: {
      type: reportForm.value.type,
      severity: reportForm.value.severity,
      description: reportForm.value.description
    }
  }

  try {
    await axios.post(API_URL, payload)

    alert('¡Reporte guardado exitosamente!')

    // Cerramos el modal y limpiamos el formulario
    isReporting.value = false
    reportForm.value.description = ''

    // Recargamos el mapa para ver el nuevo marcador
    loadIncidents()
  } catch (error) {
    const detalle = error.response?.data || error.message
    console.error('Error creando el reporte:', detalle)
    alert('Error al guardar el reporte: ' + JSON.stringify(detalle))
  }
}
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}
.instruction {
  color: #666;
  margin-bottom: 0.5rem;
}
#map {
  height: 600px;
  width: 100%;
  max-width: 1000px;
  border-radius: 12px;
  border: 2px solid #42b883;
  z-index: 1;
}

/* --- ESTILOS DEL MODAL --- */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  color: #333;
}
.modal h2 {
  margin-top: 0;
  color: #42b883;
}
.modal form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.modal label {
  font-weight: bold;
  font-size: 0.9rem;
}
.modal select, .modal textarea {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  width: 100%;
}
.modal-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
}
.btn-cancel {
  background: #f44336;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}
.btn-submit {
  background: #42b883;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}
button:hover { opacity: 0.9; }
</style>