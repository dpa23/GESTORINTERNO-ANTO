<template>
  <div class="pedidos-page">
    <div class="cabecera">
      <h2>Pedidos activos</h2>
      <button @click="mostrarConfirm = true" class="btn-cerrar-turno">Cerrar turno</button>
    </div>

    <div v-if="store.cargando">Cargando pedidos...</div>
    <div v-if="store.error" class="error">{{ store.error }}</div>

    <div v-if="!store.cargando && !store.ordenados.length" class="vacio">
      No hay pedidos activos.
    </div>

    <!-- Lista -->
    <div class="lista">
      <div
        v-for="p in store.ordenados"
        :key="p.pedido_id"
        class="pedido-card"
        :class="{ delivery: p.mozo?.toUpperCase() === 'DELIVERY' }"
      >
        <!-- Checkbox → elimina el pedido -->
        <input type="checkbox" :checked="false" @change="marcarListo(p)" class="checkbox" />

        <!-- Info -->
        <div class="info">
          <span class="nombre">{{ p.nombre }}</span>
          <span class="meta">
            {{ p.hora }} · {{ p.mozo }}
            <span v-if="p.cantidad > 1" class="cantidad">x{{ p.cantidad }}</span>
          </span>
        </div>

        <!-- Botón modificar -->
        <button @click="abrirModal(p)" class="btn-modificar">✏️</button>
      </div>
    </div>

    <!-- Modal modificar -->
    <div v-if="mostrarModal" class="modal-overlay" @click="cerrarModal">
      <div class="modal-contenido" @click.stop>
        <h3>Modificar pedido</h3>
        <div v-if="edicion" class="form-editar">
          <div class="grupo-input">
            <label>Plato:</label>
            <input v-model="edicion.nombre" type="text" />
          </div>
          <div class="grupo-input">
            <label>Cantidad:</label>
            <input v-model.number="edicion.cantidad" type="number" min="1" />
          </div>
          <div class="grupo-input">
            <label>Mozo:</label>
            <input v-model="edicion.mozo" type="text" />
          </div>
          <div class="botones-modal">
            <button @click="guardarModal" class="btn-guardar">Guardar</button>
            <button @click="cerrarModal" class="btn-cancelar">Cancelar</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirmación cerrar turno -->
    <div v-if="mostrarConfirm" class="modal-overlay" @click="mostrarConfirm = false">
      <div class="modal-contenido" @click.stop>
        <h3>¿Cerrar turno?</h3>
        <p>Se vaciará la lista de pedidos activos.</p>
        <div class="botones-modal">
          <button @click="ejecutarCerrarTurno" class="btn-guardar">Confirmar</button>
          <button @click="mostrarConfirm = false" class="btn-cancelar">Cancelar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { usePedidosStore } from "../stores/pedidos";

const store = usePedidosStore();
const mostrarModal = ref(false);
const mostrarConfirm = ref(false);
const pedidoActual = ref(null);
const edicion = ref(null);

onMounted(() => {
  store.cargarPedidos();
  store.conectarWebSocket();
});

async function marcarListo(p) {
  try {
    await store.eliminarPedido(p.pedido_id);
  } catch (e) {
    alert(e.message);
  }
}

function abrirModal(p) {
  pedidoActual.value = p;
  edicion.value = {
    nombre: p.nombre,
    cantidad: p.cantidad,
    mozo: p.mozo,
  };
  mostrarModal.value = true;
}

function cerrarModal() {
  mostrarModal.value = false;
  edicion.value = null;
  pedidoActual.value = null;
}

async function guardarModal() {
  if (!pedidoActual.value || !edicion.value) return;
  try {
    await store.editarPedido(pedidoActual.value.pedido_id, edicion.value);
    cerrarModal();
  } catch (e) {
    alert(e.message);
  }
}

async function ejecutarCerrarTurno() {
  try {
    await store.cerrarTurno();
    mostrarConfirm.value = false;
  } catch (e) {
    alert(e.message);
  }
}
</script>

<style scoped>
.pedidos-page {
  padding: 1rem;
  background: #fff5f5;
} /* ligero rosa en lugar de blanco */

.cabecera {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.btn-cerrar-turno {
  background: #c0392b;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.4rem 0.9rem;
  cursor: pointer;
  font-size: 0.85rem;
}

.lista {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.pedido-card {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.6rem 0.8rem;
  border: 1px solid #f5c2c7;
  border-radius: 8px;
  background: #fee; /* rojo suave */
} /* fondo que rima con rojo */

.pedido-card.delivery {
  background: #fffbeb;
  border-color: #f39c12;
}

.checkbox {
  width: 22px;
  height: 22px;
  cursor: pointer;
  flex-shrink: 0;
}

.info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.nombre {
  font-size: 0.95rem;
  font-weight: bold;
}
.meta {
  font-size: 0.78rem;
  color: #888;
}

.cantidad {
  font-weight: bold;
  color: #2c7a4b;
  margin-left: 0.3rem;
}

.btn-modificar {
  background: #e74c3c; /* rojo que rima con rojo */
  color: white;
  border: none;
  padding: 0.3rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}
.btn-modificar:hover {
  background: #c0392b;
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

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-contenido {
  background: #fff0f0; /* rojizo muy suave en vez de blanco */
  border-radius: 8px;
  padding: 1.5rem;
  width: 320px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
}

.modal-contenido h3 {
  margin: 0 0 1rem 0;
}
.modal-contenido p {
  color: #555;
  margin-bottom: 1rem;
}

.form-editar {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.grupo-input {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.grupo-input label {
  font-weight: bold;
  font-size: 0.9rem;
}
.grupo-input input {
  border: 1px solid #ddd;
  padding: 0.4rem;
  border-radius: 4px;
  font-size: 0.95rem;
}

.botones-modal {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.btn-guardar,
.btn-cancelar {
  flex: 1;
  padding: 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}
</style>
