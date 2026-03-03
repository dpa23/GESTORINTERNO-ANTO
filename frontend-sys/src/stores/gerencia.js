import { defineStore } from "pinia";
import { ref, computed } from "vue";

const API = "http://192.168.18.102:8000";

export const useGerenciaStore = defineStore("gerencia", () => {
  const registros = ref([]);
  const cargando = ref(false);
  const error = ref(null);

  // Filtros activos
  const filtroFecha = ref("");
  const filtroTurno = ref("");
  const filtroMozo = ref("");
  const filtroNombre = ref("");

  // ─── Carga desde backend ───────────────────────────────────────────────────
  async function cargarRegistros() {
    cargando.value = true;
    error.value = null;
    try {
      const params = new URLSearchParams();
      if (filtroFecha.value) params.append("fecha", filtroFecha.value);
      if (filtroTurno.value) params.append("turno", filtroTurno.value);
      if (filtroMozo.value) params.append("mozo", filtroMozo.value);
      if (filtroNombre.value) params.append("nombre", filtroNombre.value);

      const url = `${API}/registros${params.toString() ? "?" + params : ""}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error("Error al obtener registros.");
      const data = await res.json();
      registros.value = data.registros ?? [];
    } catch (e) {
      error.value = e.message || String(e);
    } finally {
      cargando.value = false;
    }
  }

  function limpiarFiltros() {
    filtroFecha.value = "";
    filtroTurno.value = "";
    filtroMozo.value = "";
    filtroNombre.value = "";
  }

  // ─── Computed sobre registros filtrados (client-side) ──────────────────────

  const totalVentas = computed(() => registros.value.reduce((s, r) => s + (r.cantidad ?? 1), 0));

  const porPlato = computed(() => {
    const acc = {};
    for (const r of registros.value) {
      acc[r.nombre] = (acc[r.nombre] ?? 0) + (r.cantidad ?? 1);
    }
    return Object.entries(acc)
      .map(([nombre, cantidad]) => ({ nombre, cantidad }))
      .sort((a, b) => b.cantidad - a.cantidad);
  });

  const porMozo = computed(() => {
    const acc = {};
    for (const r of registros.value) {
      const m = r.mozo ?? "?";
      acc[m] = (acc[m] ?? 0) + (r.cantidad ?? 1);
    }
    return Object.entries(acc)
      .map(([mozo, cantidad]) => ({ mozo, cantidad }))
      .sort((a, b) => b.cantidad - a.cantidad);
  });

  const porTurno = computed(() => {
    const acc = {};
    for (const r of registros.value) {
      const t = r.turno ?? "?";
      acc[t] = (acc[t] ?? 0) + (r.cantidad ?? 1);
    }
    return Object.entries(acc).map(([turno, cantidad]) => ({ turno, cantidad }));
  });

  const porFecha = computed(() => {
    const acc = {};
    for (const r of registros.value) {
      acc[r.fecha] = (acc[r.fecha] ?? 0) + (r.cantidad ?? 1);
    }
    return Object.entries(acc)
      .map(([fecha, cantidad]) => ({ fecha, cantidad }))
      .sort((a, b) => a.fecha.localeCompare(b.fecha));
  });

  // Listas únicas para los selects de filtro
  const mozosUnicos = computed(() =>
    [...new Set(registros.value.map((r) => r.mozo).filter(Boolean))].sort(),
  );
  const platosUnicos = computed(() => [...new Set(registros.value.map((r) => r.nombre))].sort());

  return {
    registros,
    cargando,
    error,
    filtroFecha,
    filtroTurno,
    filtroMozo,
    filtroNombre,
    cargarRegistros,
    limpiarFiltros,
    totalVentas,
    porPlato,
    porMozo,
    porTurno,
    porFecha,
    mozosUnicos,
    platosUnicos,
  };
});
