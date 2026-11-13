<template>
  <header class="navbar">
    <div class="brand">🚲 BiciSegura</div>
    <nav>
      <router-link to="/">Inicio</router-link>
      <!-- Más adelante agregaremos Login y Registro aquí -->
    </nav>
  </header>

  <main>
    <router-view></router-view>
  </main>
</template>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #1a1a1a;
  color: white;
  padding: 1rem 2rem;
}
.brand {
  font-size: 1.5rem;
  font-weight: bold;
  color: #42b883;
}
nav a {
  color: white;
  text-decoration: none;
  margin-left: 1rem;
}
nav a:hover {
  color: #42b883;
}
main {
  padding: 2rem;
}
</style>