<template>
  <div class="pagos-container">
    <h2 class="pagos-title">Pagos — Histórico</h2>

    <!-- Tabs: Notas / Facturas -->
    <div class="pagos-tabs">
      <Button
        :class="['tab-btn', tab === 'notas' ? 'tab-active' : 'tab-inactive']"
        label="Notas"
        icon="pi pi-file"
        @click="tab = 'notas'"
      />
      <Button
        :class="['tab-btn', tab === 'facturas' ? 'tab-active' : 'tab-inactive']"
        label="Facturas"
        icon="pi pi-receipt"
        @click="tab = 'facturas'"
      />
    </div>

    <!-- ════════ FILTROS ════════ -->
    <div class="pagos-filtros">
      <div class="filtro-item">
        <label>Cliente</label>
        <InputText v-model="filtroCliente" placeholder="Buscar por cliente..." class="w-full" />
      </div>
      <div class="filtro-item">
        <label>Nº Orden</label>
        <InputText v-model="filtroOrden" placeholder="Buscar por orden..." class="w-full" />
      </div>
      <div class="filtro-item">
        <label>IMEI (últimos 6 dígitos)</label>
        <InputText v-model="filtroImei" placeholder="Ej: 123456" maxlength="6" class="w-full" />
      </div>
      <div class="filtro-item">
        <label>Instalador</label>
        <InputText v-model="filtroInstalador" placeholder="Buscar por instalador..." class="w-full" />
      </div>
      <div class="filtro-item">
        <label>Vendedor</label>
        <InputText v-model="filtroVendedor" placeholder="Buscar por vendedor..." class="w-full" />
      </div>
    </div>

    <!-- ════════ NOTAS ════════ -->
    <div v-if="tab === 'notas'">
      <DataTable
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
            <span v-else style="color:#999;">—</span>
          </template>
        </Column>
        <Column field="total" header="Total">
          <template #body="{ data }">
            {{ data.total != null ? '$' + Number(data.total).toFixed(2) : '-' }}
          </template>
        </Column>
        <Column field="lugar_pago" header="Pagado en">
          <template #body="{ data }">
            <span v-if="data.lugar_pago" class="badge-lugar">{{ data.lugar_pago }}</span>
            <span v-else style="color:#999;">—</span>
          </template>
        </Column>
        <Column field="instalador" header="Instalador" />
        <Column field="vendedor" header="Vendedor" />
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
                @click="irDetalle('nota', data.id)" />
              <Button icon="pi pi-download" class="p-button-sm p-button-success" label="PDF"
                :loading="descargandoId === `nota-${data.id}`"
                @click="descargarPDF('nota', data)" />
              <Button icon="pi pi-trash" class="p-button-sm p-button-danger" label="Eliminar"
                @click="confirmarEliminar('nota', data)" />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- ════════ FACTURAS ════════ -->
    <div v-if="tab === 'facturas'">
      <DataTable
        :value="facturasFiltradas"
        responsiveLayout="scroll"
        :loading="loadingFacturas"
        :paginator="true"
        :rows="15"
        :rowsPerPageOptions="[15, 30, 50]"
      >
        <template #loading>
          <DataTableLoader text="Cargando facturas..." />
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
            <span v-else style="color:#999;">—</span>
          </template>
        </Column>
        <Column field="total" header="Total">
          <template #body="{ data }">
            {{ data.total != null ? '$' + Number(data.total).toFixed(2) : '-' }}
          </template>
        </Column>
        <Column field="lugar_pago" header="Pagado en">
          <template #body="{ data }">
            <span v-if="data.lugar_pago" class="badge-lugar">{{ data.lugar_pago }}</span>
            <span v-else style="color:#999;">—</span>
          </template>
        </Column>
        <Column field="instalador" header="Instalador" />
        <Column field="vendedor" header="Vendedor" />
        <Column field="status" header="Estatus">
          <template #body="{ data }">
            <span :class="'badge badge-' + badgeClassFactura(data.status)">{{ data.status }}</span>
          </template>
        </Column>
        <Column field="fecha" header="Fecha">
          <template #body="{ data }">{{ formatFecha(data.fecha) }}</template>
        </Column>
        <Column header="Acciones" style="width: 320px">
          <template #body="{ data }">
            <div style="display: flex; gap: 0.5rem;">
              <Button icon="pi pi-eye" class="p-button-sm p-button-info" label="Detalle"
                @click="irDetalle('factura', data.id)" />
              <Button icon="pi pi-download" class="p-button-sm p-button-success" label="PDF"
                :loading="descargandoId === `factura-${data.id}`"
                @click="descargarPDF('factura', data)" />
              <Button icon="pi pi-trash" class="p-button-sm p-button-danger" label="Eliminar"
                @click="confirmarEliminar('factura', data)" />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Dialogo Confirmar Eliminación -->
    <Dialog v-model:visible="showConfirmDelete" header="Confirmar Eliminación" :modal="true" :closable="false">
      <div style="padding:1.5rem; text-align:center;">
        <span>¿Seguro que deseas eliminar esta {{ eliminarTipo === 'nota' ? 'nota' : 'factura' }}?</span>
        <br />
        <small>Los reportes de servicio asociados quedarán liberados y podrán asignarse nuevamente.</small>
      </div>
      <div style="display:flex;gap:1rem;justify-content:center;padding-bottom:1rem;">
        <Button label="Eliminar" icon="pi pi-trash" class="p-button-danger" @click="ejecutarEliminar" :loading="eliminando" />
        <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary" @click="showConfirmDelete = false" />
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import DataTableLoader from '@/components/DataTableLoader.vue';
import { getNotas, getFacturas, getNotaById, getFacturaById, eliminarNota, eliminarFactura } from '@/services/pagosService';
import { generarPagoPDF } from '@/services/PagoPdfService';
import { useToast } from 'primevue/usetoast';

const router = useRouter();
const toast = useToast();

const tab = ref('notas');
const notas = ref([]);
const facturas = ref([]);
const loadingNotas = ref(false);
const loadingFacturas = ref(false);

// Filtros
const filtroCliente = ref('');
const filtroOrden = ref('');
const filtroImei = ref('');
const filtroInstalador = ref('');
const filtroVendedor = ref('');

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
  const imei6 = filtroImei.value.trim();
  const inst = filtroInstalador.value.trim().toLowerCase();
  const vend = filtroVendedor.value.trim().toLowerCase();
  if (cl) {
    result = result.filter(r => (r.cliente || '').toLowerCase().includes(cl));
  }
  if (ord) {
    result = result.filter(r => (r.ordenes || []).some(o => String(o).toLowerCase().includes(ord)));
  }
  if (imei6) {
    result = result.filter(r => getImeisUnicos(r).some(im => String(im).endsWith(imei6)));
  }
  if (inst) {
    result = result.filter(r => (r.instalador || '').toLowerCase().includes(inst));
  }
  if (vend) {
    result = result.filter(r => (r.vendedor || '').toLowerCase().includes(vend));
  }
  return result;
}

const notasFiltradas = computed(() => filtrarRegistros(notas.value));
const facturasFiltradas = computed(() => filtrarRegistros(facturas.value));

const descargandoId = ref(null);
const showConfirmDelete = ref(false);
const eliminarTipo = ref('nota');
const eliminarItem = ref(null);
const eliminando = ref(false);

function formatFecha(f) {
  if (!f) return '';
  const d = new Date(f);
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
}

function badgeClassNota(status) {
  if (status === 'pagado') return 'success';
  if (status === 'cancelado') return 'danger';
  return 'warning'; // pendiente de pago
}

function badgeClassFactura(status) {
  if (status === 'Timbrado') return 'success';
  if (status === 'Cancelado') return 'danger';
  return 'warning'; // Pendiente timbre
}

function irDetalle(tipo, id) {
  router.push({ name: 'detalle-pago', params: { tipo, id } });
}

function confirmarEliminar(tipo, item) {
  eliminarTipo.value = tipo;
  eliminarItem.value = item;
  showConfirmDelete.value = true;
}

async function ejecutarEliminar() {
  if (!eliminarItem.value) return;
  eliminando.value = true;
  try {
    if (eliminarTipo.value === 'nota') {
      await eliminarNota(eliminarItem.value.id);
      toast.add({ severity: 'success', summary: 'Eliminada', detail: 'Nota eliminada correctamente.', life: 3000 });
      await cargarNotas();
    } else {
      await eliminarFactura(eliminarItem.value.id);
      toast.add({ severity: 'success', summary: 'Eliminada', detail: 'Factura eliminada correctamente.', life: 3000 });
      await cargarFacturas();
    }
    showConfirmDelete.value = false;
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar.', life: 4000 });
  }
  eliminando.value = false;
}

async function descargarPDF(tipo, data) {
  const key = `${tipo}-${data.id}`;
  descargandoId.value = key;
  try {
    const detalle = tipo === 'nota'
      ? await getNotaById(data.id)
      : await getFacturaById(data.id);
    // El endpoint de detalle puede no devolver imeis completos, instalador ni vendedor;
    // esos campos vienen del listado (data). Se fusionan tomando el listado como fuente.
    const pdfData = {
      ...detalle,
      imeis:      getImeisUnicos(data).length ? getImeisUnicos(data) : getImeisUnicos(detalle),
      instalador: data.instalador         || detalle.instalador || '',
      vendedor:   data.vendedor           || detalle.vendedor   || '',
    };
    generarPagoPDF(tipo, pdfData);
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

async function cargarFacturas() {
  loadingFacturas.value = true;
  try {
    facturas.value = await getFacturas();
  } catch {
    facturas.value = [];
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al cargar facturas.', life: 4000 });
  }
  loadingFacturas.value = false;
}

onMounted(() => {
  cargarNotas();
  cargarFacturas();
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
}
.pagos-tabs {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1.5rem;
}
.tab-btn {
  min-width: 140px;
}
.tab-active {
  background: var(--color-title) !important;
  color: var(--color-bg) !important;
  border: none !important;
}
.tab-inactive {
  background: transparent !important;
  color: var(--color-title) !important;
  border: 2px solid var(--color-title) !important;
}
.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.85rem;
  font-weight: bold;
}
.badge-success { background: #c8e6c9; color: #256029; }
.badge-warning { background: #fff3cd; color: #856404; }
.badge-danger  { background: #f8d7da; color: #721c24; }
.badge-lugar {
  background: #e3f2fd;
  color: #1565c0;
  padding: 0.2rem 0.6rem;
  border-radius: 0.75rem;
  font-size: 0.82rem;
  font-weight: 600;
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
.imeis-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 0.85rem;
}
</style>
