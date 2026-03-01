<template>
  <div>
    <h2>Camarero</h2>

    <!-- Nombre del mozo -->
    <div class="campo-mozo">
      <label>Tu nombre:</label>
      <input v-model="mozo" type="text" placeholder="Ej: Juan" />
    </div>

    <div v-if="store.cargando">Cargando menú...</div>
    <div v-if="store.error" class="error">{{ store.error }}</div>

    <!-- Solo muestra platos con disponibles > 0 -->
    <div v-if="!Object.keys(store.platosDisponibles).length && !store.cargando" class="vacio">
      No hay platos disponibles por el momento.
    </div>

    <div v-for="cat in Object.keys(store.platosDisponibles)" :key="cat" class="categoria">
      <h3>{{ cat.replaceAll("_", " ") }}</h3>

      <div v-for="plato in store.platosDisponibles[cat]" :key="plato.id" class="plato">
        <div class="info">
          <span class="nombre">{{ plato.nombre }}</span>
          <span class="stock">{{ plato.disponibles }} disponibles</span>
        </div>

        <button @click="registrarVenta(plato)" :disabled="!mozo.trim()" class="btn-venta">
          Vender
        </button>
      </div>
    </div>

    <!-- Feedback de última venta -->
    <div v-if="ultimaVenta" class="feedback">✓ {{ ultimaVenta }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useMenuStore } from "../stores/menu";

const store = useMenuStore();
const mozo = ref("");
const ultimaVenta = ref("");

onMounted(() => {
  if (!store.categorias.length) store.cargarMenu();
});

async function registrarVenta(plato) {
  if (!mozo.value.trim()) return;

  try {
    await store.actualizarDisponibles(plato.id, -1, mozo.value.trim());
    ultimaVenta.value = `${plato.nombre} vendido por ${mozo.value.trim()}`;
    setTimeout(() => (ultimaVenta.value = ""), 3000);
  } catch (e) {
    alert(e.message);
  }
}
</script>

<style scoped>
h2 {
  margin-bottom: 1rem;
}

.campo-mozo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.campo-mozo input {
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 0.4rem 0.6rem;
  font-size: 0.95rem;
  width: 180px;
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

.info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.nombre {
  font-size: 0.95rem;
}

.stock {
  font-size: 0.78rem;
  color: #aaa;
}

.btn-venta {
  background: #2c7a4b;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.4rem 0.8rem;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-venta:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.vacio {
  color: #aaa;
  font-style: italic;
  margin-top: 1rem;
}

.feedback {
  margin-top: 1.5rem;
  padding: 0.6rem 1rem;
  background: #eafaf1;
  border: 1px solid #2c7a4b;
  border-radius: 6px;
  color: #2c7a4b;
  font-size: 0.9rem;
}
</style>
