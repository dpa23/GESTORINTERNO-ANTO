<template>
  <div>
    <h2>Caja</h2>

    <div v-if="store.cargando">Cargando menú...</div>
    <div v-if="store.error" class="error">{{ store.error }}</div>

    <!-- Turno activo -->
    <div class="turno-banner">
      Turno: <strong>{{ store.turnoActivo || "—" }}</strong>
    </div>

    <!-- Filtro rápido -->
    <div class="filtro">
      <input v-model="busqueda" type="text" placeholder="Buscar plato..." />
    </div>

    <!-- Sin resultados -->
    <div v-if="!categoriasVisibles.length && !store.cargando" class="vacio">
      No se encontraron platos.
    </div>

    <div v-for="cat in categoriasVisibles" :key="cat" class="categoria">
      <h3>{{ cat.replaceAll("_", " ") }}</h3>

      <div v-for="plato in platosFiltrados[cat]" :key="plato.id" class="plato">
        <span class="nombre">{{ plato.nombre }}</span>
        <span class="badge" :class="plato.disponibles > 0 ? 'disponible' : 'agotado'">
          {{ plato.disponibles > 0 ? plato.disponibles + " disp." : "Agotado" }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useMenuStore } from "../stores/menu";

const store = useMenuStore();
const busqueda = ref("");

onMounted(() => {
  if (!store.categorias.length) store.cargarMenu();
});

const platosFiltrados = computed(() => {
  const texto = busqueda.value.toLowerCase().trim();
  const resultado = {};

  for (const cat of store.categorias) {
    const platos = texto
      ? store.menu[cat].filter((p) => p.nombre.toLowerCase().includes(texto))
      : store.menu[cat];

    if (platos.length) resultado[cat] = platos;
  }

  return resultado;
});

const categoriasVisibles = computed(() => Object.keys(platosFiltrados.value));
</script>

<style scoped>
h2 {
  margin-bottom: 1rem;
}

.turno-banner {
  display: inline-block;
  background: #f0f9f4;
  border: 1px solid #2c7a4b;
  color: #2c7a4b;
  border-radius: 6px;
  padding: 0.4rem 0.9rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.filtro {
  margin-bottom: 1.2rem;
}

.filtro input {
  width: 100%;
  max-width: 320px;
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 0.4rem 0.7rem;
  font-size: 0.95rem;
}

.categoria {
  margin-bottom: 1.5rem;
}

h3 {
  font-size: 0.95rem;
  text-transform: uppercase;
  color: #888;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.3rem;
  margin-bottom: 0.5rem;
}

.plato {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0;
  border-bottom: 1px solid #f5f5f5;
}

.nombre {
  font-size: 0.95rem;
}

.badge {
  font-size: 0.78rem;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-weight: bold;
}

.disponible {
  background: #eafaf1;
  color: #2c7a4b;
}

.agotado {
  background: #f5f5f5;
  color: #bbb;
}

.vacio {
  color: #aaa;
  font-style: italic;
  margin-top: 1rem;
}

.error {
  color: #c0392b;
  margin-bottom: 1rem;
}
</style>
