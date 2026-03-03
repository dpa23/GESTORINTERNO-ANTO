import { defineStore } from "pinia";
import { ref, computed } from "vue";

const API = "http://192.168.18.102:8000";
const WS = "ws://192.168.18.102:8000/ws";

export const usePedidosStore = defineStore("pedidos", () => {
  const pedidos = ref([]);
  const cargando = ref(false);
  const error = ref(null);
  let socket = null;

  const ordenados = computed(() => {
    return [...pedidos.value].sort((a, b) => {
      const aDel = a.mozo?.toUpperCase() === "DELIVERY";
      const bDel = b.mozo?.toUpperCase() === "DELIVERY";
      if (aDel && !bDel) return -1;
      if (!aDel && bDel) return 1;
      return 0;
    });
  });

  async function cargarPedidos() {
    cargando.value = true;
    error.value = null;
    try {
      const res = await fetch(`${API}/pedidos_activos`);
      if (!res.ok) throw new Error("No se pudo obtener los pedidos.");
      pedidos.value = await res.json();
    } catch (e) {
      error.value = e.message || String(e);
    } finally {
      cargando.value = false;
    }
  }

  async function eliminarPedido(pedido_id) {
    const res = await fetch(`${API}/pedidos_activos/${pedido_id}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error("No se pudo eliminar el pedido.");
    pedidos.value = pedidos.value.filter((p) => p.pedido_id !== pedido_id);
  }

  async function editarPedido(pedido_id, updates) {
    const res = await fetch(`${API}/pedidos_activos/${pedido_id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    });
    if (!res.ok) throw new Error("No se pudo modificar el pedido.");
    const actualizado = await res.json();
    _reemplazarPedido(actualizado);
    return actualizado;
  }

  async function cerrarTurno() {
    const res = await fetch(`${API}/pedidos_activos/turno`, { method: "DELETE" });
    if (!res.ok) throw new Error("No se pudo cerrar el turno.");
    pedidos.value = [];
  }

  function conectarWebSocket() {
    if (socket) return;
    socket = new WebSocket(WS);

    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      if (msg.evento === "estado_inicial" && msg.pedidos_activos) {
        pedidos.value = msg.pedidos_activos;
      }
      if (msg.evento === "nuevo_pedido") {
        pedidos.value.push(msg.pedido);
        const audio = new Audio("/sounds/nuevo_pedido.mp3");
        audio.play().catch(() => {});
      }
      if (msg.evento === "pedido_actualizado") {
        _reemplazarPedido(msg.pedido);
      }
      if (msg.evento === "pedido_eliminado") {
        pedidos.value = pedidos.value.filter((p) => p.pedido_id !== msg.pedido_id);
      }
      if (msg.evento === "turno_cerrado") {
        pedidos.value = [];
      }
    };

    socket.onclose = () => {
      socket = null;
      setTimeout(conectarWebSocket, 3000);
    };
  }

  function desconectarWebSocket() {
    socket?.close();
    socket = null;
  }

  function _reemplazarPedido(actualizado) {
    const idx = pedidos.value.findIndex((p) => p.pedido_id === actualizado.pedido_id);
    if (idx !== -1) pedidos.value[idx] = actualizado;
  }

  return {
    pedidos,
    cargando,
    error,
    ordenados,
    cargarPedidos,
    eliminarPedido,
    editarPedido,
    cerrarTurno,
    conectarWebSocket,
    desconectarWebSocket,
  };
});
