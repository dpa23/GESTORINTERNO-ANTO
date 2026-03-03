<template>
  <div>
    <h2>Cocina</h2>

    <div v-if="store.cargando">Cargando menú...</div>
    <div v-if="store.error" class="error">{{ store.error }}</div>

    <!-- Filtro por categoría -->
    <div class="filtro-categoria">
      <label>Categoría:</label>
      <select v-model="categoriaFiltro">
        <option value="">Todas</option>
        <option v-for="cat in store.categorias" :key="cat" :value="cat">
          {{ cat.replaceAll("_", " ") }}
        </option>
      </select>
    </div>

    <div v-for="cat in categoriasFiltradas" :key="cat" class="categoria">
      <h3>{{ cat.replaceAll("_", " ") }}</h3>

      <div v-for="plato in store.menu[cat]" :key="plato.id" class="plato">
        <span class="nombre">{{ plato.nombre }}</span>

        <div class="controles">
          <button @click="restar(plato)" :disabled="plato.disponibles === 0">−</button>
          <span class="cantidad" :class="{ agotado: plato.disponibles === 0 }">
            {{ plato.disponibles }}
          </span>
          <button @click="sumar(plato)">+</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useMenuStore } from "../stores/menu";

const store = useMenuStore();
const categoriaFiltro = ref("");

const categoriasFiltradas = computed(() => {
  const cats = store.categorias;
  return categoriaFiltro.value ? cats.filter((c) => c === categoriaFiltro.value) : cats;
});

onMounted(() => {
  if (!store.categorias.length) store.cargarMenu();
});

async function sumar(plato) {
  try {
    await store.actualizarDisponibles(plato.id, 1);
  } catch (e) {
    alert(e.message);
  }
}

async function restar(plato) {
  try {
    await store.actualizarDisponibles(plato.id, -1);
  } catch (e) {
    alert(e.message);
  }
}
</script>

<style scoped>
h2 {
  margin-bottom: 1rem;
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

.controles {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.controles button {
  width: 28px;
  height: 28px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
}

.controles button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.cantidad {
  min-width: 28px;
  text-align: center;
  font-weight: bold;
}

.agotado {
  color: #ccc;
}

.filtro-categoria {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.filtro-categoria select {
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 0.4rem 0.6rem;
  font-size: 0.95rem;
}
</style>
