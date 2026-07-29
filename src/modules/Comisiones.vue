<template>
  <div class="comisiones-container">
    <h2 class="comisiones-title">Comprobantes — {{ tab === 'tecnico' ? 'Técnicos' : 'Vendedores' }}</h2>

    <div v-if="loading" style="text-align:center;padding:3rem;">
      <i class="pi pi-spin pi-spinner" style="font-size:2rem;"></i>
    </div>

    <template v-else>
      <!-- Pendiente = sin nota/factura todavía — mismo criterio que "pendientes" en el bot de WhatsApp. -->
      <div class="banner-pendientes" :class="{ 'sin-pendientes': !totalGeneral.reportesPendientes }">
        <i :class="totalGeneral.reportesPendientes ? 'pi pi-exclamation-triangle' : 'pi pi-check-circle'" />
        <span v-if="totalGeneral.reportesPendientes">
          <strong>{{ totalGeneral.reportesPendientes }}</strong> reporte{{ totalGeneral.reportesPendientes === 1 ? '' : 's' }} sin nota/factura,
          de <strong>{{ totalGeneral.personasConPendientes }}</strong> {{ tab === 'tecnico' ? 'técnico' : 'responsable' }}{{ totalGeneral.personasConPendientes === 1 ? '' : 's' }}.
        </span>
        <span v-else>Todos los reportes tienen nota/factura. Nada pendiente por revisar.</span>
      </div>

      <div class="filtro-mes-wrap">
        <label for="filtro-mes">Mes</label>
        <select id="filtro-mes" v-model="filtroMes" class="filtro-mes-select">
          <option value="todos">Todos</option>
          <option v-for="m in meses" :key="m.value" :value="m.value">{{ m.label }}</option>
        </select>
      </div>

      <!-- Cuántos reportes hay en total, cuántos ya tienen comprobante y cuántos faltan. -->
      <div class="resumen-card">
        <div class="resumen-item">
          <span class="resumen-label">Total de reportes</span>
          <span class="resumen-valor">{{ totalGeneral.totalReportes }}</span>
        </div>
        <div class="resumen-item">
          <span class="resumen-label">Reportes con comprobante</span>
          <span class="resumen-valor con">{{ totalGeneral.reportesConComprobante }}</span>
          <span v-if="tab === 'vendedor'" class="resumen-subvalor">{{ formatTotal(totalGeneral.vendidoConComprobante) }} vendido</span>
        </div>
        <div class="resumen-item">
          <span class="resumen-label">Reportes sin nota/factura</span>
          <span class="resumen-valor sin">{{ totalGeneral.reportesPendientes }}</span>
          <span v-if="tab === 'vendedor'" class="resumen-subvalor">{{ formatTotal(totalGeneral.vendidoSinNota) }} vendido</span>
        </div>
      </div>

      <div v-if="!personas.length" class="vacio">No hay {{ tab === 'tecnico' ? 'técnicos' : 'vendedores' }} con reportes registrados.</div>

      <div class="grid-container">
        <button
          v-for="(p, idx) in personasOrdenadas"
          :key="p.nombre"
          type="button"
          class="persona-card"
          :class="{ 'persona-card-top': tab === 'tecnico' && idx < 3 }"
          @click="verDetalle(p.nombre)"
        >
          <span v-if="tab === 'tecnico' && idx < 3" class="persona-rank" :class="'rank-' + (idx + 1)">{{ idx + 1 }}</span>
          <span class="persona-nombre">{{ p.nombre }}</span>

          <span class="persona-vendido">{{ p.reportesConComprobante }}<span class="persona-vendido-de">/{{ p.totalReportes }}</span></span>
          <span class="persona-sub">
            reportes con comprobante<template v-if="tab === 'vendedor'"> · {{ formatTotal(p.totalVendido) }} vendido</template>
          </span>
          <span v-if="p.reportesSinNota > 0" class="pendiente-tag">
            <i class="pi pi-exclamation-triangle" />
            {{ p.reportesSinNota }} sin nota{{ p.reportesSinNota === 1 ? '' : 's' }}
          </span>
          <span v-else class="al-dia-tag">
            <i class="pi pi-check-circle" /> Todo con nota/factura
          </span>
        </button>
      </div>

      <!-- Sin actividad todavía: una sección compacta, no una tarjeta cada uno. -->
      <div v-if="personasSinActividad.length" class="cero-section">
        <span class="cero-titulo">
          <i class="pi pi-inbox" /> Sin actividad todavía ({{ personasSinActividad.length }})
        </span>
        <div class="cero-chips">
          <button v-for="p in personasSinActividad" :key="p.nombre" type="button" class="chip-cero" @click="verDetalle(p.nombre)">
            {{ p.nombre }}
            <span class="chip-cero-sub">{{ p.totalReportes }}</span>
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useLoginStore } from '@/stores/loginStore';
import { getReportesServicioTodos } from '@/services/reportesService';
import { getNotas, getFacturas } from '@/services/pagosService';
import { indexarNotasFacturas, agruparPorPersona, mesesDisponibles, filtrarPorMes, mesActual } from '@/utils/comisiones';

const route = useRoute();
const router = useRouter();
const loginStore = useLoginStore();
const user = computed(() => loginStore.user || {});

const loading = ref(true);
// ?tab=tecnico|vendedor en la URL — cada menú (Técnicos / Vendedores) apunta
// a su propio link. No hay selector interno: para cambiar de vista hay que
// volver al menú, así quedan separadas y no se mezclan por accidente.
const tab = computed(() => (route.query.tab === 'vendedor' ? 'vendedor' : 'tecnico'));
const filtroMes = ref('todos');
const reportes = ref([]);
const notas = ref([]);
const facturas = ref([]);

const meses = computed(() => mesesDisponibles(reportes.value));
const reportesFiltradosPorMes = computed(() => filtrarPorMes(reportes.value, filtroMes.value));
const indice = computed(() => indexarNotasFacturas(notas.value, facturas.value));

const formatoMoneda = new Intl.NumberFormat('es-MX', {
  style: 'currency', currency: 'MXN', minimumFractionDigits: 2, maximumFractionDigits: 2,
});
function formatTotal(value) {
  return formatoMoneda.format(Number(value) || 0);
}

const personas = computed(() => {
  const campo = tab.value === 'tecnico' ? 'nombre_instalador' : 'vendedor';
  return agruparPorPersona(reportesFiltradosPorMes.value, indice.value, campo);
});

// "Pendiente" = sin nota/factura todavía — mismo criterio que usa el
// comando "pendientes" del bot de WhatsApp (no cuenta "con nota pero sin
// comprobante" como pendiente, eso queda solo como dato aparte en el detalle).
function tienePendientes(p) {
  return p.reportesSinNota > 0;
}
// Actividad = tiene reportes, punto — no depende de dinero. Un técnico con
// reportes pero $0 de comisión capturada (dato faltante) sigue siendo
// alguien con trabajo pendiente de revisar, no "sin actividad".
function actividad(p) {
  return p.totalReportes;
}

// Ordenado por el número que se ve en la tarjeta — reportes CON comprobante,
// no dinero. Empate: desempata por cuántos le faltan nota/factura.
const personasOrdenadas = computed(() => {
  const conActividad = personas.value.filter(p => actividad(p) > 0);
  return [...conActividad].sort((a, b) => {
    if (tab.value === 'vendedor') {
      // Vendedor/Responsable: el más atrasado (sin nota) va primero.
      return b.reportesSinNota - a.reportesSinNota || b.reportesConComprobante - a.reportesConComprobante;
    }
    return b.reportesConComprobante - a.reportesConComprobante || b.reportesSinNota - a.reportesSinNota;
  });
});

const personasSinActividad = computed(() =>
  personas.value.filter(p => actividad(p) <= 0).sort((a, b) => a.nombre.localeCompare(b.nombre))
);

const totalGeneral = computed(() => {
  return personas.value.reduce((acc, p) => {
    acc.totalReportes += p.totalReportes;
    acc.vendido += p.totalVendido;
    acc.vendidoConComprobante += p.totalConComprobante;
    acc.vendidoSinNota += p.totalSinNota;
    acc.reportesConComprobante += p.reportesConComprobante;
    acc.reportesPendientes += p.reportesSinNota;
    if (tienePendientes(p)) acc.personasConPendientes += 1;
    return acc;
  }, { totalReportes: 0, vendido: 0, vendidoConComprobante: 0, vendidoSinNota: 0, reportesConComprobante: 0, reportesPendientes: 0, personasConPendientes: 0 });
});

function verDetalle(nombre) {
  router.push({ name: 'detalle-comision', params: { tipo: tab.value, nombre } });
}

async function cargar() {
  loading.value = true;
  try {
    [reportes.value, notas.value, facturas.value] = await Promise.all([
      getReportesServicioTodos(),
      getNotas(),
      getFacturas(),
    ]);
  } catch {
    reportes.value = [];
    notas.value = [];
    facturas.value = [];
  }
  // Default: mes en curso, si hay datos de este mes. Si no, mejor "Todos"
  // que una tabla vacía sin explicación.
  const actual = mesActual();
  filtroMes.value = meses.value.some(m => m.value === actual) ? actual : 'todos';
  loading.value = false;
}

// Un Técnico solo debe ver su propia comisión, no la lista completa.
onMounted(async () => {
  if ((user.value.perfil || '') === 'Tecnico') {
    router.replace({ name: 'detalle-comision', params: { tipo: 'tecnico', nombre: user.value.username } });
    return;
  }
  await cargar();
});
</script>

<style scoped>
.comisiones-container {
  margin: 1.5rem auto;
  padding: 1.5rem 2rem;
  max-width: none;
  width: 100%;
  box-sizing: border-box;
}
.comisiones-title {
  text-align: center;
  margin-bottom: 1.5rem;
  color: var(--color-title);
}
.banner-pendientes {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  padding: 0.85rem 1.25rem;
  margin-bottom: 1.5rem;
  border-radius: 12px;
  font-size: 0.92rem;
  font-weight: 600;
  background: color-mix(in srgb, var(--color-warning) 16%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-warning) 40%, transparent);
  color: var(--color-warning);
}
.banner-pendientes.sin-pendientes {
  background: color-mix(in srgb, var(--color-success) 14%, transparent);
  border-color: color-mix(in srgb, var(--color-success) 40%, transparent);
  color: var(--color-success);
}
.filtro-mes-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}
.filtro-mes-wrap label {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--color-text);
  opacity: 0.75;
}
.filtro-mes-select {
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  border: 1px solid var(--color-border);
  background: var(--color-card);
  color: var(--color-text);
  font-size: 0.9rem;
}
.resumen-card {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 2rem;
  padding: 1.25rem;
  margin-bottom: 1rem;
  border-radius: 14px;
  background: var(--color-card);
  border: 1px solid var(--color-border);
}
.resumen-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
}
.resumen-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text);
  opacity: 0.7;
}
.resumen-valor {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-title);
}
.resumen-valor.con { color: var(--color-success); }
.resumen-valor.sin { color: var(--color-warning); }
.resumen-subvalor {
  font-size: 0.78rem;
  color: var(--color-text);
  opacity: 0.65;
}
.vacio {
  text-align: center;
  padding: 2rem;
  color: var(--color-text);
  opacity: 0.7;
}
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.25rem;
}
.persona-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.3rem;
  padding: 1.25rem;
  border-radius: 14px;
  background: var(--color-card);
  border: 1px solid var(--color-border);
  cursor: pointer;
  text-align: left;
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
}
.persona-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-2, 0 8px 20px rgba(0, 0, 0, 0.09));
}
.persona-card-top {
  border-color: color-mix(in srgb, var(--color-primary) 45%, var(--color-border));
}
.persona-rank {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 800;
  color: #fff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
}
.rank-1 { background: #d4af37; }
.rank-2 { background: #a8adb4; }
.rank-3 { background: #b06a3a; }
.persona-nombre {
  font-weight: 700;
  font-size: 1.05rem;
  color: var(--color-title);
}
.persona-vendido {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--color-title);
}
.persona-vendido-de {
  font-size: 1rem;
  font-weight: 600;
  opacity: 0.5;
}
.persona-sub {
  font-size: 0.78rem;
  color: var(--color-text);
  opacity: 0.65;
  margin-bottom: 0.3rem;
}
.pendiente-tag {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
  background: color-mix(in srgb, var(--color-warning) 20%, transparent);
  color: var(--color-warning);
}
.al-dia-tag {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
  background: color-mix(in srgb, var(--color-success) 18%, transparent);
  color: var(--color-success);
}
.cero-section {
  margin-top: 2rem;
  padding-top: 1.25rem;
  border-top: 1px dashed var(--color-border);
}
.cero-titulo {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--color-text);
  opacity: 0.7;
  margin-bottom: 0.75rem;
}
.cero-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.chip-cero {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: var(--color-card);
  color: var(--color-text);
  opacity: 0.75;
  cursor: pointer;
  font-size: 0.82rem;
  transition: opacity 0.15s, border-color 0.15s;
}
.chip-cero:hover {
  opacity: 1;
  border-color: var(--color-primary);
}
.chip-cero-sub {
  font-size: 0.7rem;
  padding: 0.05rem 0.4rem;
  border-radius: 999px;
  background: var(--color-border);
}

@media (max-width: 768px) {
  .comisiones-container {
    margin: 1rem auto;
    padding: 1rem 0.75rem;
  }
}
</style>
