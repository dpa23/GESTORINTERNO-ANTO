<template>
  <div id="app">
    <nav>
      <img src="./assets/logoanto.jpeg" alt="Anto" class="logo" />
      <RouterLink to="/cocina"> Cocina </RouterLink>
      <RouterLink to="/camarero"> Camarero </RouterLink>
      <RouterLink to="/caja"> Caja </RouterLink>
    </nav>

    <div class="turno" v-if="store.turnoActivo">
      Turno activo: <strong>{{ store.turnoActivo }}</strong>
    </div>

    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from "vue";
import { RouterLink, RouterView } from "vue-router";
import { useMenuStore } from "./stores/menu";

const store = useMenuStore();

onMounted(() => {
  store.conectarWebSocket();
});

onUnmounted(() => {
  store.desconectarWebSocket();
});
</script>

<style scoped>
#app {
  font-family: sans-serif;
  max-width: 960px;
  margin: 0 auto;
  padding: 1rem;
  background-color: #e8e8e8;
  color: #000;
}

nav {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

nav a {
  text-decoration: none;
  color: #555;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
}

nav a.router-link-active {
  background: #f30a0a;
  color: white;
  font-weight: bold;
}

.turno {
  font-size: 0.85rem;
  color: #888;
  margin-bottom: 1rem;
}
.logo {
  height: 40px;
  object-fit: contain;
}
</style>
