import { defineStore } from "pinia";
import { ref, computed } from "vue";

const API = "http://10.49.145.106:8000";
const WS = "ws://10.49.145.106:8000/ws";

export const useMenuStore = defineStore("menu", () => {
  // ─── Estado ────────────────────────────────────────────────────────────────
  const menu = ref({});
  const turnoActivo = ref("");
  const cargando = ref(false);
  const error = ref(null);
  let socket = null;

  // ─── Getters ───────────────────────────────────────────────────────────────

  // Todas las categorías del menú sin 'core'
  const categorias = computed(() => Object.keys(menu.value).filter((k) => k !== "core"));

  // Solo platos con disponibles > 0
  const platosDisponibles = computed(() => {
    const resultado = {};
    for (const cat of categorias.value) {
      const filtrados = menu.value[cat].filter((p) => p.disponibles > 0);
      if (filtrados.length) resultado[cat] = filtrados;
    }
    return resultado;
  });

  // ─── Acciones ──────────────────────────────────────────────────────────────

  async function cargarMenu() {
    cargando.value = true;
    error.value = null;
    try {
      const res = await fetch(`${API}/menu`);
      const data = await res.json();
      menu.value = data.menu;
      turnoActivo.value = data.turno_activo;
    } catch (e) {
      error.value = "No se pudo conectar con el servidor.";
    } finally {
      cargando.value = false;
    }
  }

  async function actualizarDisponibles(plato_id, delta, mozo = null) {
    const body = { delta };
    if (mozo) body.mozo = mozo;

    const res = await fetch(`${API}/menu/${plato_id}/disponibles`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail);
    }

    return await res.json();
  }

  function conectarWebSocket() {
    if (socket) return; // ya conectado

    socket = new WebSocket(WS);

    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      if (msg.evento === "estado_inicial") {
        menu.value = msg.menu;
        turnoActivo.value = msg.turno_activo;
      }

      if (msg.evento === "disponible_actualizado") {
        // Actualizar solo el plato afectado sin recargar todo
        for (const cat of categorias.value) {
          const plato = menu.value[cat]?.find((p) => p.id === msg.plato_id);
          if (plato) {
            plato.disponibles = msg.nuevos_disponibles;
            break;
          }
        }
      }
    };

    socket.onclose = () => {
      socket = null;
      // Reconectar tras 3 segundos si se cae
      setTimeout(conectarWebSocket, 3000);
    };
  }

  function desconectarWebSocket() {
    socket?.close();
    socket = null;
  }

  return {
    menu,
    turnoActivo,
    cargando,
    error,
    categorias,
    platosDisponibles,
    cargarMenu,
    actualizarDisponibles,
    conectarWebSocket,
    desconectarWebSocket,
  };
});
