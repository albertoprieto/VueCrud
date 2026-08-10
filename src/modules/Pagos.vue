<template>
  <div class="pagos-container">
    <h2 class="pagos-title">
      <i class="pi pi-file"></i>
      Notas — Histórico
    </h2>

    <!-- ════════ FILTROS ════════ -->
    <button
      v-if="isMobile"
      type="button"
      class="filtros-toggle"
      @click="filtrosAbiertos = !filtrosAbiertos"
    >
      <span><i class="pi pi-filter" /> Filtros<span v-if="filtrosActivos" class="filtros-badge">{{ filtrosActivos }}</span></span>
      <i :class="['pi', filtrosAbiertos ? 'pi-chevron-up' : 'pi-chevron-down']" />
    </button>

    <div class="pagos-filtros" v-if="!isMobile || filtrosAbiertos">
      <div class="filtro-item">
        <label>Cliente</label>
        <InputText v-model="filtroCliente" placeholder="Buscar por cliente..." class="w-full" />
      </div>
      <div class="filtro-item">
        <label>Nº Orden</label>
        <InputText v-model="filtroOrden" placeholder="Buscar por orden..." class="w-full" />
      </div>
      <div class="filtro-item">
        <label>IMEI</label>
        <InputText v-model="filtroImei" placeholder="Buscar por IMEI..." class="w-full" />
      </div>
      <div class="filtro-item">
        <label>Instalador</label>
        <InputText v-model="filtroInstalador" placeholder="Buscar por instalador..." class="w-full" />
      </div>
      <div class="filtro-item">
        <label>Vendedor</label>
        <InputText v-model="filtroVendedor" placeholder="Buscar por vendedor..." class="w-full" />
      </div>
      <div class="filtro-item">
        <label>Cuenta</label>
        <InputText v-model="filtroCuenta" placeholder="Buscar por cuenta..." class="w-full" />
      </div>
      <div class="filtro-item">
        <label>Pagado en</label>
        <Dropdown
          v-model="filtroLugarPago"
          :options="lugaresPago"
          placeholder="Todos"
          showClear
          class="w-full"
        />
      </div>
    </div>

    <!-- ════════ NOTAS ════════ -->
    <div class="tabla-seccion seccion-notas">
      <DataTable
        v-if="!isMobile"
        :value="notasFiltradas"
        responsiveLayout="scroll"
        :loading="loadingNotas"
        :paginator="true"
        :rows="15"
        :rowsPerPageOptions="[15, 30, 50]"
      >
        <template #loading>
          <DataTableLoader text="Cargando notas..." />
        </template>
        <Column field="id" header="ID" style="width: 60px" />
        <Column header="Órdenes">
          <template #body="{ data }">
            {{ (data.ordenes || []).join(', ') }}
          </template>
        </Column>
        <Column field="cliente" header="Cliente" />
        <Column header="IMEIs">
          <template #body="{ data }">
            <div v-if="getImeisUnicos(data).length" class="imeis-cell">
              <div v-for="(imei, idx) in getImeisUnicos(data)" :key="idx">{{ imei }}</div>
            </div>
            <span v-else style="color:var(--color-border);">—</span>
          </template>
        </Column>
        <Column field="total" header="Total">
          <template #body="{ data }">
            {{ formatTotal(data.total) }}
          </template>
        </Column>
        <Column field="lugar_pago" header="Pagado en">
          <template #body="{ data }">
            <span v-if="data.lugar_pago" class="badge-lugar">{{ data.lugar_pago }}</span>
            <span v-else style="color:var(--color-border);">—</span>
          </template>
        </Column>
        <Column field="instalador" header="Instalador" />
        <Column field="vendedor" header="Vendedor" />
        <Column field="cuenta" header="Cuenta" />
        <Column field="status" header="Estatus">
          <template #body="{ data }">
            <span :class="'badge badge-' + badgeClassNota(data.status)">{{ data.status }}</span>
          </template>
        </Column>
        <Column field="fecha" header="Fecha">
          <template #body="{ data }">{{ formatFecha(data.fecha) }}</template>
        </Column>
        <Column header="Acciones" style="width: 320px">
          <template #body="{ data }">
            <div style="display: flex; gap: 0.5rem;">
              <Button icon="pi pi-eye" class="p-button-sm p-button-info" label="Detalle"
                @click="irDetalle(data.id)" />
              <Button icon="pi pi-download" class="p-button-sm p-button-success" label="PDF"
                :loading="descargandoId === data.id"
                @click="descargarPDF(data)" />
              <Button icon="pi pi-file" class="p-button-sm p-button-info p-button-outlined" label="Comprobante"
                :disabled="!parseComprobantes(data).length"
                @click="verComprobante(data)" />
              <Button icon="pi pi-trash" class="p-button-sm p-button-danger" label="Eliminar"
                @click="confirmarEliminar(data)" />
            </div>
          </template>
        </Column>
      </DataTable>

      <div v-else class="mobile-list-wrap">
        <div v-if="loadingNotas" class="mobile-loader-wrap">
          <DataTableLoader text="Cargando notas..." />
        </div>
        <div v-else-if="!notasFiltradas.length" class="mobile-empty">
          No hay notas para mostrar.
        </div>
        <div v-else class="mobile-cards">
          <article
            v-for="item in notasFiltradas"
            :key="`nota-mobile-${item.id}`"
            class="mobile-card"
          >
            <header class="mobile-card-header">
              <div>
                <p class="mobile-card-id">Nota #{{ item.id }}</p>
                <p class="mobile-card-cliente">{{ item.cliente || 'Sin cliente' }}</p>
              </div>
              <span :class="'badge badge-' + badgeClassNota(item.status)">{{ item.status }}</span>
            </header>

            <div class="mobile-card-grid">
              <div class="mobile-field">
                <span class="mobile-label">Total</span>
                <span class="mobile-value">{{ formatTotal(item.total) }}</span>
              </div>
              <div class="mobile-field">
                <span class="mobile-label">Fecha</span>
                <span class="mobile-value">{{ formatFecha(item.fecha) }}</span>
              </div>
              <div class="mobile-field">
                <span class="mobile-label">Ordenes</span>
                <span class="mobile-value">{{ (item.ordenes || []).join(', ') || '—' }}</span>
              </div>
              <div class="mobile-field">
                <span class="mobile-label">Pagado en</span>
                <span class="mobile-value">{{ item.lugar_pago || '—' }}</span>
              </div>
              <div class="mobile-field">
                <span class="mobile-label">Instalador</span>
                <span class="mobile-value">{{ item.instalador || '—' }}</span>
              </div>
              <div class="mobile-field">
                <span class="mobile-label">Vendedor</span>
                <span class="mobile-value">{{ item.vendedor || '—' }}</span>
              </div>
              <div class="mobile-field">
                <span class="mobile-label">Cuenta</span>
                <span class="mobile-value">{{ item.cuenta || '—' }}</span>
              </div>
              <div class="mobile-field mobile-field-full">
                <span class="mobile-label">IMEIs</span>
                <span class="mobile-value">{{ getImeisUnicos(item).join(', ') || '—' }}</span>
              </div>
            </div>

            <div class="mobile-actions">
              <Button icon="pi pi-eye" class="p-button-sm p-button-info" label="Detalle"
                @click="irDetalle(item.id)" />
              <Button icon="pi pi-download" class="p-button-sm p-button-success" label="PDF"
                :loading="descargandoId === item.id"
                @click="descargarPDF(item)" />
              <Button icon="pi pi-file" class="p-button-sm p-button-info p-button-outlined" label="Comprobante"
                :disabled="!parseComprobantes(item).length"
                @click="verComprobante(item)" />
              <Button icon="pi pi-trash" class="p-button-sm p-button-danger" label="Eliminar"
                @click="confirmarEliminar(item)" />
            </div>
          </article>
        </div>
      </div>
    </div>

    <!-- Dialogo Confirmar Eliminación -->
    <Dialog v-model:visible="showConfirmDelete" header="Confirmar Eliminación" :modal="true" :closable="false">
      <div style="padding:1.5rem; text-align:center;">
        <span>¿Seguro que deseas eliminar esta nota?</span>
        <br />
        <small>Los reportes de servicio asociados quedarán liberados y podrán asignarse nuevamente.</small>
      </div>
      <div style="display:flex;gap:1rem;justify-content:center;padding-bottom:1rem;">
        <Button label="Eliminar" icon="pi pi-trash" class="p-button-danger" @click="ejecutarEliminar" :loading="eliminando" />
        <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary" @click="showConfirmDelete = false" />
      </div>
    </Dialog>

    <!-- Dialogo Comprobantes -->
    <Dialog v-model:visible="showComprobantes" header="Comprobantes de pago" :modal="true" :style="{ width: '420px', maxWidth: '95vw' }" :draggable="false">
      <div v-if="!comprobantesActivos.length" style="text-align:center;color:var(--color-border);padding:1rem;">
        Sin comprobantes cargados.
      </div>
      <div v-else class="comprobantes-lista">
        <div v-for="(comp, idx) in comprobantesActivos" :key="idx" class="comprobante-item">
          <i class="pi pi-file" style="color:var(--color-primary);margin-right:0.5rem;"></i>
          <a :href="urlComprobante(comp)" target="_blank" rel="noopener noreferrer" class="comprobante-link">
            {{ nombreArchivoComprobante(comp) }}
          </a>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import DataTableLoader from '@/components/DataTableLoader.vue';
import { getNotas, getNotaById, eliminarNota } from '@/services/pagosService';
import { generarPagoPDF } from '@/services/PagoPdfService';
import { useToast } from 'primevue/usetoast';

const router = useRouter();
const toast = useToast();

const notas = ref([]);
const loadingNotas = ref(false);
const isMobile = ref(false);

// Filtros
const filtroCliente = ref('');
const filtroOrden = ref('');
const filtroImei = ref('');
const filtroInstalador = ref('');
const filtroVendedor = ref('');
const filtroCuenta = ref('');
const filtroLugarPago = ref('');
const filtrosAbiertos = ref(false);

const filtrosActivos = computed(() => {
  return [filtroCliente.value, filtroOrden.value, filtroImei.value, filtroInstalador.value, filtroVendedor.value, filtroCuenta.value, filtroLugarPago.value]
    .filter(v => (v || '').trim()).length;
});

const lugaresPago = [
 'ASP Vianey',
 'ASP Renovaciones',
 'Comercializadora',
 'BBVA PAU',
 'Mercadopago Victor',
 'MercadoLibre Eliseo',
 'Efectivo entregado oficina'
];

function parseImeis(value) {
  if (Array.isArray(value)) return value;
  if (typeof value !== 'string') return [];

  const raw = value.trim();
  if (!raw) return [];

  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return raw.includes(',') ? raw.split(',') : [];
  }
}

function getImeisUnicos(row) {
  const arr = parseImeis(row?.imeis)
    .map(v => String(v).trim())
    .filter(Boolean);

  return Array.from(new Set(arr));
}

function filtrarRegistros(rows) {
  let result = rows;
  const cl = filtroCliente.value.trim().toLowerCase();
  const ord = filtroOrden.value.trim().toLowerCase();
  const imei = filtroImei.value.trim();
  const inst = filtroInstalador.value.trim().toLowerCase();
  const vend = filtroVendedor.value.trim().toLowerCase();
  const cuenta = filtroCuenta.value.trim().toLowerCase();
  if (cl) {
    result = result.filter(r => (r.cliente || '').toLowerCase().includes(cl));
  }
  if (ord) {
    result = result.filter(r => (r.ordenes || []).some(o => String(o).toLowerCase().includes(ord)));
  }
  if (imei) {
    result = result.filter(r => getImeisUnicos(r).some(im => String(im).includes(imei)));
  }
  if (inst) {
    result = result.filter(r => (r.instalador || '').toLowerCase().includes(inst));
  }
  if (vend) {
    result = result.filter(r => (r.vendedor || '').toLowerCase().includes(vend));
  }
  if (cuenta) {
    result = result.filter(r => (r.cuenta || '').toLowerCase().includes(cuenta));
  }
  if (filtroLugarPago.value) {
    result = result.filter(r => (r.lugar_pago || '') === filtroLugarPago.value);
  }
  return result;
}

const notasFiltradas = computed(() => filtrarRegistros(notas.value));

const descargandoId = ref(null);
const showConfirmDelete = ref(false);
const eliminarItem = ref(null);
const eliminando = ref(false);

const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
const showComprobantes = ref(false);
const comprobantesActivos = ref([]);

function parseComprobantes(row) {
  const raw = row?.comprobantes;
  if (Array.isArray(raw)) return raw;
  if (typeof raw !== 'string' || !raw.trim()) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function urlComprobante(path) {
  if (!path) return '';
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${API_URL}${p}`;
}

function nombreArchivoComprobante(path) {
  if (!path) return 'comprobante';
  return path.split('/').pop();
}

function verComprobante(row) {
  const comps = parseComprobantes(row);
  if (!comps.length) return;
  if (comps.length === 1) {
    window.open(urlComprobante(comps[0]), '_blank', 'noopener');
    return;
  }
  comprobantesActivos.value = comps;
  showComprobantes.value = true;
}

function formatFecha(f) {
  if (!f) return '';
  const d = new Date(f);
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
}

const formatoMoneda = new Intl.NumberFormat('es-MX', {
  style: 'currency',
  currency: 'MXN',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

function formatTotal(value) {
  return value != null ? formatoMoneda.format(Number(value)) : '-';
}

function setViewportMode() {
  isMobile.value = window.innerWidth <= 768;
}

function badgeClassNota(status) {
  if (status === 'pagado') return 'success';
  if (status === 'cancelado') return 'danger';
  return 'warning'; // pendiente de pago
}

function irDetalle(id) {
  router.push({ name: 'detalle-pago', params: { tipo: 'nota', id } });
}

function confirmarEliminar(item) {
  eliminarItem.value = item;
  showConfirmDelete.value = true;
}

async function ejecutarEliminar() {
  if (!eliminarItem.value) return;
  eliminando.value = true;
  try {
    await eliminarNota(eliminarItem.value.id);
    toast.add({ severity: 'success', summary: 'Eliminada', detail: 'Nota eliminada correctamente.', life: 3000 });
    await cargarNotas();
    showConfirmDelete.value = false;
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar.', life: 4000 });
  }
  eliminando.value = false;
}

async function descargarPDF(data) {
  descargandoId.value = data.id;
  try {
    const detalle = await getNotaById(data.id);
    // El endpoint de detalle puede no devolver imeis completos, instalador ni vendedor;
    // esos campos vienen del listado (data). Se fusionan tomando el listado como fuente.
    const pdfData = {
      ...detalle,
      imeis:      getImeisUnicos(data).length ? getImeisUnicos(data) : getImeisUnicos(detalle),
      instalador: data.instalador         || detalle.instalador || '',
      vendedor:   data.vendedor           || detalle.vendedor   || '',
    };
    generarPagoPDF('nota', pdfData);
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo generar el PDF.', life: 4000 });
  }
  descargandoId.value = null;
}

async function cargarNotas() {
  loadingNotas.value = true;
  try {
    notas.value = await getNotas();
  } catch {
    notas.value = [];
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al cargar notas.', life: 4000 });
  }
  loadingNotas.value = false;
}

onMounted(() => {
  setViewportMode();
  window.addEventListener('resize', setViewportMode);
  cargarNotas();
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', setViewportMode);
});
</script>

<style scoped>
.pagos-container {
  margin: 2rem auto;
  padding: 2rem 1.5rem;
}
.pagos-title {
  text-align: center;
  margin-bottom: 1.5rem;
  color: var(--color-title);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}
.tabla-seccion {
  border-top: 3px solid var(--accent-seccion);
  padding-top: 1rem;
}
.seccion-notas {
  --accent-seccion: #2a78d6;
}
.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.85rem;
  font-weight: bold;
}
.badge-success { background: color-mix(in srgb, var(--color-success) 22%, transparent); color: var(--color-success); }
.badge-warning { background: color-mix(in srgb, var(--color-warning) 25%, transparent); color: var(--color-warning); }
.badge-danger  { background: color-mix(in srgb, var(--color-error) 20%, transparent); color: var(--color-error); }
.badge-lugar {
  background: color-mix(in srgb, var(--color-primary) 20%, transparent);
  color: var(--color-primary);
  padding: 0.2rem 0.6rem;
  border-radius: 0.75rem;
  font-size: 0.82rem;
  font-weight: 600;
}
.filtros-toggle {
  display: none;
}
.pagos-filtros {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.filtro-item {
  flex: 1;
  min-width: 180px;
}
.filtro-item label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.3rem;
  font-size: 0.85rem;
}
.comprobantes-lista {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.comprobante-item {
  display: flex;
  align-items: center;
  padding: 0.4rem 0;
  border-bottom: 1px solid var(--color-border);
}
.comprobante-item:last-child {
  border-bottom: none;
}
.comprobante-link {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
}
.imeis-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 0.85rem;
}

.mobile-list-wrap {
  margin-top: 0.5rem;
}

.mobile-loader-wrap,
.mobile-empty {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1rem;
}

.mobile-empty {
  text-align: center;
  color: var(--color-text);
}

.mobile-cards {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.mobile-card {
  border: 1px solid var(--color-border);
  background: var(--color-card);
  border-radius: 12px;
  padding: 0.9rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.mobile-card-header {
  display: flex;
  justify-content: space-between;
  gap: 0.8rem;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.mobile-card-id {
  margin: 0;
  font-size: 0.78rem;
  color: var(--color-text);
  font-weight: 600;
}

.mobile-card-cliente {
  margin: 0.2rem 0 0;
  font-weight: 700;
  color: var(--color-title);
}

.mobile-card-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.6rem;
  margin-bottom: 0.8rem;
}

.mobile-field {
  min-width: 0;
}

.mobile-field-full {
  grid-column: 1 / -1;
}

.mobile-label {
  display: block;
  font-size: 0.72rem;
  color: var(--color-text);
  margin-bottom: 0.15rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.mobile-value {
  display: block;
  font-size: 0.88rem;
  color: var(--color-text);
  word-break: break-word;
}

.mobile-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .pagos-container {
    margin: 1rem auto;
    padding: 1rem 0.75rem;
  }

  .filtros-toggle {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    border: 1px solid var(--color-border);
    border-radius: 10px;
    background: var(--color-card);
    color: var(--color-title);
    font-weight: 600;
    font-size: 0.95rem;
  }
  .filtros-toggle span {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .filtros-badge {
    background: var(--color-primary);
    color: var(--color-on-primary, #fff);
    font-size: 0.72rem;
    font-weight: 700;
    border-radius: 999px;
    min-width: 1.3rem;
    height: 1.3rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0 0.3rem;
  }

  .pagos-filtros {
    gap: 0.75rem;
    padding: 0.9rem;
    margin-top: -0.5rem;
    border: 1px solid var(--color-border);
    border-radius: 10px;
    background: var(--color-bg-light);
  }

  .filtro-item {
    min-width: 100%;
  }
}
</style>
