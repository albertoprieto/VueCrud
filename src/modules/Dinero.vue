<template>
  <div class="dinero-container">
    <h2>Resumen de Dinero</h2>
    <div class="dinero-dashboard">
      <div class="dinero-card ingreso">
        <h3>Ingresos</h3>
        <p class="dinero-monto">{{ formatoMoneda(totalIngresos) }}</p>
      </div>
      <div class="dinero-card egreso">
        <h3>Egresos</h3>
        <p class="dinero-monto">{{ formatoMoneda(totalEgresos) }}</p>
      </div>
      <div class="dinero-card saldo">
        <h3>Saldo</h3>
        <p class="dinero-monto">{{ formatoMoneda(saldo) }}</p>
      </div>
    </div>
    <h3>Movimientos</h3>
    <div v-if="error" class="dinero-error">{{ error }}</div>
    <div v-else>
      <DataTable :value="movimientos" :paginator="true" :rows="10" class="dinero-table" :loading="cargando">
        <Column field="fecha" header="Fecha" sortable />
        <Column field="tipo" header="Tipo" sortable />
        <Column field="concepto" header="Concepto" sortable />
        <Column field="monto" header="Monto" :body="formatoMoneda" sortable />
        <Column field="referencia" header="Referencia" />
        <Column header="Acciones">
          <template #body="slotProps">
            <!-- Ver comprobante si existe para esta referencia -->
            <a v-if="urlComprobanteMovimiento(slotProps.data)" :href="urlComprobanteMovimiento(slotProps.data)" target="_blank" rel="noopener noreferrer">
              <Button
                icon="pi pi-download"
                class="p-button-sm p-button-secondary mr-2"
                label="Ver comprobante"
              />
            </a>
            <Button
              icon="pi pi-trash"
              class="p-button-sm p-button-danger"
              label="Eliminar"
              @click="eliminarMovimiento(slotProps.data)"
            />
          </template>
        </Column>
        <template #empty>
          <div class="dinero-empty">No hay movimientos registrados.</div>
        </template>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import axios from 'axios';
import { getTodosReportes } from '@/services/reportesServicio.js';
import { getAsignacionesTecnicos } from '@/services/asignacionesService.js';
import { getVentas } from '@/services/ventasService.js';

const movimientos = ref([]);
const cargando = ref(false);
const error = ref("");

const cargarMovimientos = async () => {
  cargando.value = true;
  error.value = "";
  try {
    const apiUrl = import.meta.env.VITE_API_URL || '';
    const res = await axios.get(`${apiUrl}/movimientos-dinero`);
    if (Array.isArray(res.data)) {
      movimientos.value = res.data;
    } else {
      movimientos.value = [];
      error.value = "Respuesta inesperada del servidor.";
    }
  } catch (e) {
    movimientos.value = [];
    error.value = "No se pudo cargar la información. Intenta más tarde.";
  }
  cargando.value = false;
};

const eliminarMovimiento = async (movimiento) => {
  cargando.value = true;
  try {
    const apiUrl = import.meta.env.VITE_API_URL || '';
    await axios.delete(`${apiUrl}/movimientos-dinero/${movimiento.id}`);
    await cargarMovimientos();
    error.value = '';
  } catch (e) {
    error.value = 'No se pudo eliminar el movimiento.';
  }
  cargando.value = false;
};

const comprobantesMap = ref({});
const reportesCache = ref([]);

const cargarComprobantesMap = async () => {
  try {
    const [reportes, asignaciones, ventas] = await Promise.all([
      getTodosReportes(),
      getAsignacionesTecnicos(),
      getVentas()
    ]);
    reportesCache.value = Array.isArray(reportes) ? reportes : [];
    const map = {};
    for (const r of reportesCache.value) {
      if (r && r.comprobante_path) {
        const path = r.comprobante_path;
        map[`ReporteServicio-${r.id}`] = path;
        map[String(r.id)] = path;
        const asig = asignaciones.find(a => a.id == r.asignacion_id);
        if (asig && asig.venta_id) {
          const v = Array.isArray(ventas) ? ventas.find(x => x.id == asig.venta_id) : null;
          const folioVenta = v ? (v.folio || (v.id ? `SO-${String(v.id).padStart(5, '0')}` : '')) : '';
          if (folioVenta) map[folioVenta] = path;
        }
        const parts = String(path).split('/');
        if (parts.length >= 3) {
          const folioServicio = parts[2];
          if (folioServicio) map[folioServicio] = path;
        }
      }
    }
    comprobantesMap.value = map;
  } catch (e) {
    // Silencio
  }
};

const apiOrigin = (() => {
  try {
    const u = new URL(import.meta.env.VITE_API_URL || window.location.origin);
    return u.origin;
  } catch {
    return '';
  }
})();

const urlComprobanteMovimiento = (mov) => {
  const ref = (mov && mov.referencia ? String(mov.referencia) : '').trim();
  if (!ref) return '';
  let path = comprobantesMap.value[ref];
  if (!path) {
    const lowerRef = ref.toLowerCase();
    const key = Object.keys(comprobantesMap.value).find(k => k && k.toLowerCase() === lowerRef);
    if (key) path = comprobantesMap.value[key];
  }
  if (!path) {
    const key = Object.keys(comprobantesMap.value).find(k => {
      const a = (k || '').toLowerCase();
      const b = ref.toLowerCase();
      return a && (a.includes(b) || b.includes(a));
    });
    if (key) path = comprobantesMap.value[key];
  }
  // Fallback: buscar por substring en cualquier comprobante_path
  if (!path && Array.isArray(reportesCache.value)) {
    const encontrado = reportesCache.value.find(r => String(r.comprobante_path || '').toLowerCase().includes(ref.toLowerCase()));
    if (encontrado) path = encontrado.comprobante_path;
  }
  if (!path) return '';
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${apiOrigin}${p}`;
};

onMounted(async () => {
  await Promise.all([
    cargarMovimientos(),
    cargarComprobantesMap()
  ]);
});

const totalIngresos = computed(() => movimientos.value.filter(m => m.tipo === 'Ingreso').reduce((acc, m) => acc + Number(m.monto), 0));
const totalEgresos = computed(() => movimientos.value.filter(m => m.tipo === 'Egreso').reduce((acc, m) => acc + Number(m.monto), 0));
const saldo = computed(() => totalIngresos.value - totalEgresos.value);

const formatoMoneda = (valor) => {
  return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(Number(valor) || 0);
};
</script>

<style scoped>
.dinero-container {
  max-width: 900px;
  margin: 2rem auto;
  background: var(--color-bg, #23272f);
  color: var(--color-text, #fff);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  padding: 2rem 1.5rem;
}
.dinero-dashboard {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
}
.dinero-card {
  flex: 1;
  background: #23232b;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  text-align: center;
}
.dinero-card.ingreso { border-left: 6px solid #43a047; }
.dinero-card.egreso { border-left: 6px solid #e53935; }
.dinero-card.saldo { border-left: 6px solid #ffb300; }
.dinero-monto {
  font-size: 2rem;
  font-weight: bold;
  margin: 0.5rem 0 0 0;
}
.dinero-table {
  margin-top: 1rem;
}
.dinero-error {
  color: #e53935;
  background: #fff3f3;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1rem;
  text-align: center;
}
.dinero-empty {
  color: #bbb;
  text-align: center;
  padding: 2rem 0;
}
</style>
