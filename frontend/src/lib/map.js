import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import theft from '../assets/markers/theft.svg'
import accident from '../assets/markers/accident.svg'
import pothole from '../assets/markers/pothole.svg'
import roadwork from '../assets/markers/roadwork.svg'
import flooding from '../assets/markers/flooding.svg'
import other from '../assets/markers/other.svg'
import fallback from '../assets/markers/default.svg'

export const API = 'http://127.0.0.1:8000/api'

const ICONS = { theft, pothole, accident, roadwork, flooding, other }

// Tipos de incidente: valor del backend, etiqueta e ícono
export const TYPES = [
  { v: 'theft', l: 'Robo' }, { v: 'pothole', l: 'Bache' }, { v: 'accident', l: 'Accidente' },
  { v: 'roadwork', l: 'Obra' }, { v: 'flooding', l: 'Inundación' }, { v: 'other', l: 'Otro' }
].map((t) => ({ ...t, icon: ICONS[t.v] }))
export const SEVERITY = { low: 'Baja', medium: 'Media', high: 'Alta' }

export const iconFor = (t) =>
  L.icon({ iconUrl: ICONS[t] || fallback, iconSize: [32, 42], iconAnchor: [16, 42], popupAnchor: [0, -38] })

export function createMap(el) {
  const map = L.map(el, { zoomControl: false }).setView([4.6097, -74.0817], 12)
  // OpenStreetMap no requiere API key; el tema oscuro se aplica con CSS (style.css)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, attribution: '© OpenStreetMap'
  }).addTo(map)
  // Recalcula el tamaño si el contenedor cambia (evita mapas en blanco o cortados)
  new ResizeObserver(() => map.invalidateSize()).observe(el)
  return map
}
// Punto de color para origen, destino y posición actual
export const dot = (map, ll, color, r = 9) =>
  L.circleMarker(ll, { radius: r, color: '#fff', weight: 2, fillColor: color, fillOpacity: 1 }).addTo(map)

export { L }
