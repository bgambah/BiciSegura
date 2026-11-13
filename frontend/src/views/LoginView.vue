<template>
  <div class="page auth">
    <h1>¡Qué bueno verte de nuevo!</h1>
    <p class="muted">Tu ciudad. Tu bici. Tu ruta segura.</p>
    <div class="seg">
      <button :class="{ on: !reg }" @click="reg = false">Iniciar sesión</button>
      <button :class="{ on: reg }" @click="reg = true">Registrarse</button>
    </div>
    <form @submit.prevent="send">
      <template v-if="reg"><label>Nombre completo</label><input v-model="f.full_name" required /></template>
      <label>Correo electrónico</label><input v-model="f.email" type="email" placeholder="nombre@correo.com" required />
      <label>Contraseña</label><input v-model="f.password" type="password" minlength="8" required />
      <p v-if="err" class="err">{{ err }}</p>
      <button class="btn">{{ reg ? 'Crear cuenta' : 'Iniciar sesión' }}</button>
    </form>
    <button type="button" class="btn ghost" @click="guest">Entrar sin iniciar sesión (solo pruebas)</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { API } from '../lib/map'

const router = useRouter()
const reg = ref(false)
const err = ref('')
const f = ref({ full_name: '', email: '', password: '' })

function guest() {
  localStorage.setItem('guest', '1')
  router.push('/')
}

async function send() {
  err.value = ''
  try {
    if (reg.value) await axios.post(`${API}/auth/register/`, f.value)
    const { data } = await axios.post(`${API}/auth/login/`, { email: f.value.email, password: f.value.password })
    localStorage.setItem('token', data.access)
    router.push('/')
  } catch (e) {
    err.value = JSON.stringify(e.response?.data || e.message)
  }
}
</script>
