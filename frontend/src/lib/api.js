import axios from 'axios'
import router from '../router'
import { API } from './map'

export const api = axios.create({ baseURL: API })

// Envía el token si hay sesión. Si el token venció (401), vuelve al inicio de sesión.
api.interceptors.request.use((c) => {
  const t = localStorage.getItem('token')
  if (t) c.headers.Authorization = `Bearer ${t}`
  return c
})
api.interceptors.response.use((r) => r, (e) => {
  if (e.response?.status === 401 && localStorage.getItem('token')) router.push('/login')
  return Promise.reject(e)
})

export const hasToken = () => !!localStorage.getItem('token')

export const errMsg = (e) =>
  e.response?.data?.detail ||
  (e.response ? JSON.stringify(e.response.data) : `No pudimos conectar con el servidor (${API}). Revisa que el backend esté corriendo.`)

export const KINDS = { safest: 'Más segura', fastest: 'Más rápida', bikeways: 'Más ciclorrutas' }
export const STATUS = { active: 'En marcha', paused: 'En pausa', finished: 'Finalizado' }

export const kmText = (m) => (m < 1000 ? `${m} m` : `${(m / 1000).toFixed(1)} km`)
export const minText = (s) => `${Math.max(1, Math.round(s / 60))} min`
// Color según el índice de seguridad (0 peligrosa, 100 segura)
export const tone = (i) => (i >= 75 ? 'ok' : i >= 50 ? 'warn' : 'bad')
