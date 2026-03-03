<template>
  <div class="gerencia-wrap">
    <!-- ── Header ─────────────────────────────────────────────────────── -->
    <header class="g-header">
      <h1>Dashboard Gerencia</h1>
      <span class="turno-badge">{{ fechaHoy }}</span>
    </header>

    <!-- ── Panel de filtros ───────────────────────────────────────────── -->
    <section class="filtros-panel">
      <div class="filtro-grupo">
        <label>Fecha</label>
        <input type="date" v-model="store.filtroFecha" @change="store.cargarRegistros()" />
      </div>
      <div class="filtro-grupo">
        <label>Turno</label>
        <select v-model="store.filtroTurno" @change="store.cargarRegistros()">
          <option value="">Todos</option>
          <option value="Mañana">Mañana</option>
          <option value="Tarde">Tarde</option>
        </select>
      </div>
      <div class="filtro-grupo">
        <label>Mozo</label>
        <select v-model="store.filtroMozo" @change="store.cargarRegistros()">
          <option value="">Todos</option>
          <option v-for="m in store.mozosUnicos" :key="m" :value="m">{{ m }}</option>
        </select>
      </div>
      <div class="filtro-grupo">
        <label>Platillo</label>
        <input
          type="text"
          v-model="store.filtroNombre"
          placeholder="Buscar platillo..."
          @input="debounceCargar()"
        />
      </div>
      <button class="btn-limpiar" @click="limpiarYRecargar()">✕ Limpiar</button>
    </section>

    <!-- ── Estado ─────────────────────────────────────────────────────── -->
    <div v-if="store.cargando" class="estado-msg">Cargando datos…</div>
    <div v-if="store.error" class="estado-msg error">{{ store.error }}</div>

    <!-- ── KPIs ──────────────────────────────────────────────────────── -->
    <section v-if="!store.cargando && !store.error" class="kpis">
      <div class="kpi-card">
        <span class="kpi-num">{{ store.totalVentas }}</span>
        <span class="kpi-label">Unidades vendidas</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-num">{{ store.registros.length }}</span>
        <span class="kpi-label">Registros totales</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-num kpi-small">{{ store.porPlato[0]?.nombre ?? "—" }}</span>
        <span class="kpi-label">Platillo más vendido</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-num">{{ store.porMozo[0]?.mozo ?? "—" }}</span>
        <span class="kpi-label">Mozo con más ventas</span>
      </div>
    </section>

    <!-- ── Gráficos ───────────────────────────────────────────────────── -->
    <section v-if="!store.cargando && store.registros.length" class="graficos-grid">
      <!-- Demanda por platillo -->
      <div class="grafico-card wide">
        <h2>Demanda por platillo</h2>
        <div class="chart-scroll">
          <div v-for="item in store.porPlato" :key="item.nombre" class="barra-row">
            <span class="barra-label" :title="item.nombre">{{ item.nombre }}</span>
            <div class="barra-track">
              <div
                class="barra-fill"
                :style="{ width: barWidth(item.cantidad, maxPlato) + '%' }"
              ></div>
            </div>
            <span class="barra-val">{{ item.cantidad }}</span>
          </div>
        </div>
      </div>

      <!-- Línea de ventas por fecha -->
      <div class="grafico-card" v-if="store.porFecha.length > 1">
        <h2>Ventas por fecha</h2>
        <svg class="linechart" viewBox="0 0 400 180" preserveAspectRatio="none">
          <polyline
            :points="linePoints"
            fill="none"
            stroke="#c0392b"
            stroke-width="2.5"
            stroke-linejoin="round"
          />
          <circle
            v-for="(pt, i) in linePointsArr"
            :key="'c' + i"
            :cx="pt.x"
            :cy="pt.y"
            r="4"
            fill="#c0392b"
          />
          <text
            v-for="(pt, i) in linePointsArr"
            :key="'lx' + i"
            :x="pt.x"
            y="175"
            text-anchor="middle"
            font-size="9"
            fill="#888"
          >
            {{ pt.label }}
          </text>
          <text
            v-for="(pt, i) in linePointsArr"
            :key="'ly' + i"
            :x="pt.x"
            :y="pt.y - 8"
            text-anchor="middle"
            font-size="9"
            fill="#333"
          >
            {{ pt.val }}
          </text>
        </svg>
      </div>

      <!-- Donut por turno -->
      <div class="grafico-card" v-if="store.porTurno.length">
        <h2>Ventas por turno</h2>
        <div class="donut-wrap">
          <svg viewBox="0 0 120 120" class="donut-svg">
            <circle cx="60" cy="60" r="45" fill="none" stroke="#eee" stroke-width="20" />
            <circle
              v-for="(seg, i) in donutSegments"
              :key="i"
              cx="60"
              cy="60"
              r="45"
              fill="none"
              :stroke="seg.color"
              stroke-width="20"
              :stroke-dasharray="`${seg.dash} ${seg.gap}`"
              :stroke-dashoffset="seg.offset"
              transform="rotate(-90 60 60)"
            />
          </svg>
          <div class="donut-legend">
            <div v-for="(seg, i) in donutSegments" :key="i" class="legend-row">
              <span class="legend-dot" :style="{ background: seg.color }"></span>
              <span
                >{{ seg.turno }}: <strong>{{ seg.cantidad }}</strong></span
              >
            </div>
          </div>
        </div>
      </div>

      <!-- Barras por mozo -->
      <div class="grafico-card" v-if="store.porMozo.length">
        <h2>Ventas por mozo</h2>
        <div v-for="item in store.porMozo" :key="item.mozo" class="barra-row">
          <span class="barra-label">{{ item.mozo }}</span>
          <div class="barra-track">
            <div
              class="barra-fill mozo-fill"
              :style="{ width: barWidth(item.cantidad, maxMozo) + '%' }"
            ></div>
          </div>
          <span class="barra-val">{{ item.cantidad }}</span>
        </div>
      </div>
    </section>

    <!-- Sin datos -->
    <div v-if="!store.cargando && !store.error && !store.registros.length" class="estado-msg">
      Sin registros para los filtros seleccionados.
    </div>

    <!-- ── Tabla detalle ──────────────────────────────────────────────── -->
    <section v-if="store.registros.length" class="tabla-section">
      <h2>Detalle de registros</h2>
      <div class="tabla-scroll">
        <table>
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Hora</th>
              <th>Turno</th>
              <th>Mozo</th>
              <th>Platillo</th>
              <th>Cant.</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in store.registros" :key="i">
              <td>{{ r.fecha }}</td>
              <td>{{ r.hora }}</td>
              <td>
                <span :class="['badge-turno', r.turno === 'Mañana' ? 'manana' : 'tarde']">
                  {{ r.turno }}
                </span>
              </td>
              <td>{{ r.mozo }}</td>
              <td>{{ r.nombre }}</td>
              <td class="center">{{ r.cantidad }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { useGerenciaStore } from "@/stores/gerencia";

const store = useGerenciaStore();

const fechaHoy = new Date().toLocaleDateString("es-PE", {
  weekday: "long",
  day: "numeric",
  month: "long",
  year: "numeric",
});

onMounted(() => store.cargarRegistros());

// Debounce para búsqueda por nombre
let debTimer = null;
function debounceCargar() {
  clearTimeout(debTimer);
  debTimer = setTimeout(() => store.cargarRegistros(), 400);
}

function limpiarYRecargar() {
  store.limpiarFiltros();
  store.cargarRegistros();
}

// Barras
const maxPlato = computed(() => store.porPlato[0]?.cantidad ?? 1);
const maxMozo = computed(() => store.porMozo[0]?.cantidad ?? 1);
function barWidth(val, max) {
  return max === 0 ? 0 : Math.max(4, Math.round((val / max) * 100));
}

// SVG línea por fecha
const linePointsArr = computed(() => {
  const data = store.porFecha;
  if (!data.length) return [];
  const maxVal = Math.max(...data.map((d) => d.cantidad));
  const W = 400,
    H = 160,
    PAD = 30;
  return data.map((d, i) => ({
    x: PAD + (i / Math.max(data.length - 1, 1)) * (W - PAD * 2),
    y: PAD + (1 - d.cantidad / maxVal) * (H - PAD * 2),
    val: d.cantidad,
    label: d.fecha.slice(5),
  }));
});
const linePoints = computed(() => linePointsArr.value.map((p) => `${p.x},${p.y}`).join(" "));

// Donut por turno
const CIRCUMFERENCE = 2 * Math.PI * 45;
const COLORES = ["#c0392b", "#2980b9", "#27ae60", "#f39c12"];
const donutSegments = computed(() => {
  const data = store.porTurno;
  const total = data.reduce((s, d) => s + d.cantidad, 0);
  if (!total) return [];
  let offsetAcum = 0;
  return data.map((d, i) => {
    const dash = (d.cantidad / total) * CIRCUMFERENCE;
    const seg = {
      turno: d.turno,
      cantidad: d.cantidad,
      color: COLORES[i % COLORES.length],
      dash,
      gap: CIRCUMFERENCE - dash,
      offset: -offsetAcum,
    };
    offsetAcum += dash;
    return seg;
  });
});
</script>

<style scoped>
.gerencia-wrap {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1.2rem 1rem 3rem;
  font-family: "Segoe UI", sans-serif;
  color: #222;
}
.g-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.2rem;
}
.g-header h1 {
  font-size: 1.4rem;
  font-weight: 700;
  margin: 0;
}
.turno-badge {
  background: #c0392b;
  color: #fff;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  text-transform: capitalize;
}
.filtros-panel {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  align-items: flex-end;
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 1.4rem;
}
.filtro-grupo {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  flex: 1;
  min-width: 140px;
}
.filtro-grupo label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #555;
}
.filtro-grupo input,
.filtro-grupo select {
  padding: 0.45rem 0.7rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 0.85rem;
  background: #fff;
}
.btn-limpiar {
  padding: 0.45rem 1rem;
  background: #e74c3c;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  align-self: flex-end;
}
.btn-limpiar:hover {
  background: #c0392b;
}
.kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.9rem;
  margin-bottom: 1.6rem;
}
.kpi-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 1rem 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
.kpi-num {
  font-size: 1.5rem;
  font-weight: 700;
  color: #c0392b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.kpi-small {
  font-size: 1rem;
}
.kpi-label {
  font-size: 0.75rem;
  color: #777;
}
.graficos-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}
.grafico-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 1.1rem 1.2rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
.grafico-card.wide {
  grid-column: 1 / -1;
}
.grafico-card h2 {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0 0 0.9rem;
  color: #333;
}
.chart-scroll {
  max-height: 340px;
  overflow-y: auto;
}
.barra-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.45rem;
}
.barra-label {
  width: 180px;
  min-width: 180px;
  font-size: 0.78rem;
  color: #444;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.barra-track {
  flex: 1;
  background: #f0f0f0;
  border-radius: 4px;
  height: 14px;
  overflow: hidden;
}
.barra-fill {
  height: 100%;
  background: #c0392b;
  border-radius: 4px;
  transition: width 0.3s;
}
.mozo-fill {
  background: #2980b9;
}
.barra-val {
  font-size: 0.78rem;
  font-weight: 600;
  width: 24px;
  text-align: right;
}
.linechart {
  width: 100%;
  height: 180px;
}
.donut-wrap {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}
.donut-svg {
  width: 120px;
  height: 120px;
  flex-shrink: 0;
}
.donut-legend {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.legend-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.82rem;
}
.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}
.tabla-section h2 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.7rem;
}
.tabla-scroll {
  overflow-x: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}
thead tr {
  background: #f4f4f4;
}
th,
td {
  padding: 0.55rem 0.8rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}
th {
  font-weight: 600;
  color: #555;
}
tbody tr:hover {
  background: #fafafa;
}
.center {
  text-align: center;
}
.badge-turno {
  display: inline-block;
  padding: 0.15rem 0.55rem;
  border-radius: 12px;
  font-size: 0.73rem;
  font-weight: 600;
}
.manana {
  background: #fff3cd;
  color: #856404;
}
.tarde {
  background: #cfe2ff;
  color: #084298;
}
.estado-msg {
  text-align: center;
  padding: 2rem;
  color: #888;
  font-size: 0.9rem;
}
.estado-msg.error {
  color: #c0392b;
}
@media (max-width: 700px) {
  .graficos-grid {
    grid-template-columns: 1fr;
  }
  .grafico-card.wide {
    grid-column: 1;
  }
  .barra-label {
    width: 110px;
    min-width: 110px;
  }
}
</style>
