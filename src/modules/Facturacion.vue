<template>
  <div class="fact-container">
    <h2 class="fact-title"><i class="pi pi-receipt" /> Facturación</h2>

    <div class="fact-toolbar">
      <div class="fact-search">
        <i class="pi pi-search" />
        <InputText v-model="filtroCliente" placeholder="Buscar por cliente..." />
      </div>
      <div class="fact-search">
        <i class="pi pi-mobile" />
        <InputText v-model="filtroImei" placeholder="Buscar por IMEI..." />
      </div>
      <div class="filtro-estado">
        <button
          v-for="op in opcionesEstado"
          :key="op.value"
          type="button"
          class="estado-chip"
          :class="{ activo: filtroEstado === op.value }"
          @click="filtroEstado = op.value"
        >
          {{ op.label }}
          <span class="estado-chip-count">{{ contarPorEstado(op.value) }}</span>
        </button>
      </div>
    </div>

    <div class="fact-table-card">
      <DataTable
        v-if="!isMobile"
        :value="facturasFiltradas"
        responsiveLayout="scroll"
        :loading="loading"
        :paginator="facturasFiltradas.length > 15"
        :rows="15"
      >
        <template #loading><DataTableLoader text="Cargando facturas..." /></template>
        <Column field="id" header="ID" style="width:60px" />
        <Column field="cliente" header="Cliente" />
        <Column header="Órdenes">
          <template #body="{ data }">{{ (data.ordenes || []).join(', ') || '—' }}</template>
        </Column>
        <Column header="IMEIs">
          <template #body="{ data }">{{ getImeisUnicos(data).join(', ') || '—' }}</template>
        </Column>
        <Column header="Total">
          <template #body="{ data }"><span class="celda-total">{{ formatTotal(data.total) }}</span></template>
        </Column>
        <Column header="Estatus">
          <template #body="{ data }">
            <span :class="'badge badge-' + badgeClass(data.status)">{{ data.status }}</span>
          </template>
        </Column>
        <Column header="Fecha">
          <template #body="{ data }">{{ formatFecha(data.fecha) }}</template>
        </Column>
        <Column header="Antigüedad">
          <template #body="{ data }">
            <span v-if="data.status === 'Pendiente timbre'" class="antiguedad-pill" :class="claseAntiguedad(data.fecha)">
              {{ diasPendiente(data.fecha) }} día{{ diasPendiente(data.fecha) === 1 ? '' : 's' }}
            </span>
            <span v-else class="celda-vacia">—</span>
          </template>
        </Column>
        <Column header="Acciones" style="width:220px">
          <template #body="{ data }">
            <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
              <Button
                v-if="data.status === 'Pendiente timbre'"
                icon="pi pi-verified" label="Timbrar"
                class="p-button-sm p-button-success"
                @click="irDetalle(data.id)"
              />
              <Button v-else icon="pi pi-eye" label="Detalle" class="p-button-sm p-button-info" @click="irDetalle(data.id)" />
              <Button
                icon="pi pi-trash" class="p-button-sm p-button-danger p-button-outlined"
                v-if="data.status === 'Pendiente timbre'"
                @click="confirmarEliminar(data)"
              />
            </div>
          </template>
        </Column>
      </DataTable>

      <div v-else class="mobile-list-wrap">
        <div v-if="loading" class="mobile-loader-wrap"><DataTableLoader text="Cargando facturas..." /></div>
        <div v-else-if="!facturasFiltradas.length" class="mobile-empty">No hay facturas para mostrar.</div>
        <div v-else class="mobile-cards">
          <article v-for="item in facturasFiltradas" :key="item.id" class="mobile-card" @click="irDetalle(item.id)">
            <header class="mobile-card-header">
              <div>
                <p class="mobile-card-id">Factura #{{ item.id }}</p>
                <p class="mobile-card-cliente">{{ item.cliente || 'Sin cliente' }}</p>
              </div>
              <span :class="'badge badge-' + badgeClass(item.status)">{{ item.status }}</span>
            </header>
            <div class="mobile-card-grid">
              <div class="mobile-field"><span class="mobile-label">Total</span><span class="mobile-value">{{ formatTotal(item.total) }}</span></div>
              <div class="mobile-field"><span class="mobile-label">Fecha</span><span class="mobile-value">{{ formatFecha(item.fecha) }}</span></div>
              <div class="mobile-field mobile-field-full"><span class="mobile-label">IMEIs</span><span class="mobile-value">{{ getImeisUnicos(item).join(', ') || '—' }}</span></div>
              <div v-if="item.status === 'Pendiente timbre'" class="mobile-field">
                <span class="mobile-label">Antigüedad</span>
                <span class="antiguedad-pill" :class="claseAntiguedad(item.fecha)">{{ diasPendiente(item.fecha) }} día{{ diasPendiente(item.fecha) === 1 ? '' : 's' }}</span>
              </div>
            </div>
          </article>
        </div>
      </div>
    </div>

    <Dialog v-model:visible="showConfirmDelete" header="Eliminar prefactura" :modal="true" :closable="false">
      <div style="padding:1rem;text-align:center;">
        <span>¿Eliminar esta prefactura? Los reportes de servicio quedarán libres para agregarse a otra.</span>
      </div>
      <div style="display:flex;gap:1rem;justify-content:center;padding-bottom:1rem;">
        <Button label="Eliminar" icon="pi pi-trash" class="p-button-danger" :loading="eliminando" @click="ejecutarEliminar" />
        <Button label="Cancelar" class="p-button-secondary" @click="showConfirmDelete = false" />
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
import DataTableLoader from '@/components/DataTableLoader.vue';
import { useToast } from 'primevue/usetoast';
import { useLoginStore } from '@/stores/loginStore';
import { getFacturas, eliminarFactura } from '@/services/pagosService';

const router = useRouter();
const toast = useToast();
const loginStore = useLoginStore();
const esAdmin = computed(() => (loginStore.user?.perfil || '').toLowerCase() === 'admin');

const facturas = ref([]);
const loading = ref(true);
const isMobile = ref(false);
const filtroCliente = ref('');
const filtroImei = ref('');
const filtroEstado = ref('todos');

const opcionesEstado = [
  { value: 'todos', label: 'Todas' },
  { value: 'Pendiente timbre', label: 'Pendientes' },
  { value: 'Timbrado', label: 'Timbradas' },
  { value: 'Cancelado', label: 'Canceladas' },
];

function contarPorEstado(valor) {
  if (valor === 'todos') return facturas.value.length;
  return facturas.value.filter(f => f.status === valor).length;
}

function getImeisUnicos(row) {
  const arr = (Array.isArray(row?.imeis) ? row.imeis : []).map(v => String(v).trim()).filter(Boolean);
  return Array.from(new Set(arr));
}

const facturasFiltradas = computed(() => {
  const cl = filtroCliente.value.trim().toLowerCase();
  const imei = filtroImei.value.trim();
  return facturas.value.filter(f => {
    if (filtroEstado.value !== 'todos' && f.status !== filtroEstado.value) return false;
    if (cl && !(f.cliente || '').toLowerCase().includes(cl)) return false;
    if (imei && !getImeisUnicos(f).some(im => im.includes(imei))) return false;
    return true;
  });
});

const formatoMoneda = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', minimumFractionDigits: 2, maximumFractionDigits: 2 });
function formatTotal(v) { return v != null ? formatoMoneda.format(Number(v)) : '-'; }
function formatFecha(f) {
  if (!f) return '';
  const d = new Date(f);
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
}
function badgeClass(status) {
  if (status === 'Timbrado') return 'success';
  if (status === 'Cancelado') return 'danger';
  return 'warning';
}

function irDetalle(id) {
  router.push({ name: 'detalle-factura', params: { id } });
}

const showConfirmDelete = ref(false);
const eliminarItem = ref(null);
const eliminando = ref(false);
function confirmarEliminar(item) {
  eliminarItem.value = item;
  showConfirmDelete.value = true;
}
async function ejecutarEliminar() {
  if (!eliminarItem.value) return;
  eliminando.value = true;
  try {
    await eliminarFactura(eliminarItem.value.id);
    toast.add({ severity: 'success', summary: 'Eliminada', detail: 'Prefactura eliminada.', life: 3000 });
    showConfirmDelete.value = false;
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo eliminar.', life: 4000 });
  }
  eliminando.value = false;
}

async function cargar() {
  loading.value = true;
  try {
    facturas.value = await getFacturas();
  } catch {
    facturas.value = [];
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar las facturas.', life: 4000 });
  }
  loading.value = false;
}

function setViewportMode() { isMobile.value = window.innerWidth <= 768; }

function diasPendiente(fecha) {
  if (!fecha) return 0;
  const dias = (Date.now() - new Date(fecha).getTime()) / 86400000;
  return Math.max(0, Math.floor(dias));
}
function claseAntiguedad(fecha) {
  const d = diasPendiente(fecha);
  if (d >= 15) return 'antiguedad-critica';
  if (d >= 7) return 'antiguedad-media';
  return '';
}

onMounted(() => {
  if (!esAdmin.value) {
    router.replace('/');
    return;
  }
  setViewportMode();
  window.addEventListener('resize', setViewportMode);
  cargar();
});
onBeforeUnmount(() => window.removeEventListener('resize', setViewportMode));
</script>

<style scoped>
.fact-container { margin: 2rem auto; padding: 2rem 1.5rem; }
.fact-title {
  display: flex; align-items: center; justify-content: center; gap: 0.6rem;
  color: var(--color-title); margin-bottom: 1.75rem;
  font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em;
}
.fact-title .pi { color: var(--color-primary); }

.fact-toolbar {
  display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center;
  margin-bottom: 1.5rem; padding: 1rem 1.1rem; border-radius: 16px;
  background: var(--color-card); border: 1px solid var(--color-border);
  box-shadow: var(--shadow-1, 0 1px 4px rgba(0, 0, 0, 0.04));
}
.fact-search {
  position: relative; flex: 1; min-width: 220px; display: flex; align-items: center;
}
.fact-search .pi {
  position: absolute; left: 0.9rem; color: var(--color-text); opacity: 0.5; font-size: 0.9rem; pointer-events: none;
}
.fact-search :deep(input) {
  width: 100%; padding-left: 2.4rem; border-radius: 10px;
  background: var(--color-bg-light, transparent);
}
.filtro-estado { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.estado-chip {
  display: flex; align-items: center; gap: 0.4rem;
  padding: 0.45rem 1rem; border-radius: 999px;
  border: 1px solid var(--color-border); background: transparent; color: var(--color-text);
  cursor: pointer; font-size: 0.83rem; font-weight: 600;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}
.estado-chip:hover { border-color: var(--color-primary); }
.estado-chip.activo { background: var(--color-primary); border-color: var(--color-primary); color: var(--color-on-primary, #fff); }
.estado-chip-count {
  opacity: 0.85; font-weight: 700; font-size: 0.72rem;
  background: color-mix(in srgb, currentColor 16%, transparent);
  padding: 0.05rem 0.45rem; border-radius: 999px;
}

.fact-table-card {
  background: var(--color-card); border: 1px solid var(--color-border);
  border-radius: 16px; overflow: hidden;
  box-shadow: var(--shadow-1, 0 1px 4px rgba(0, 0, 0, 0.04));
}
.fact-table-card :deep(.p-datatable-header),
.fact-table-card :deep(th) {
  background: var(--color-bg-light, transparent);
  font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.03em;
}
.fact-table-card :deep(tr:hover td) {
  background: color-mix(in srgb, var(--color-primary) 5%, transparent);
}
.celda-total { font-weight: 700; color: var(--color-title); }
.celda-vacia { color: var(--color-border); }

.badge {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.3rem 0.8rem; border-radius: 999px; font-size: 0.78rem; font-weight: 700;
}
.badge::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.badge-success { background: color-mix(in srgb, var(--color-success) 18%, transparent); color: var(--color-success); }
.badge-warning { background: color-mix(in srgb, var(--color-warning) 20%, transparent); color: var(--color-warning); }
.badge-danger  { background: color-mix(in srgb, var(--color-error) 16%, transparent); color: var(--color-error); }

.antiguedad-pill {
  display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px;
  font-size: 0.78rem; font-weight: 700;
  background: color-mix(in srgb, var(--color-success) 14%, transparent); color: var(--color-success);
}
.antiguedad-pill.antiguedad-media { background: color-mix(in srgb, var(--color-warning) 18%, transparent); color: var(--color-warning); }
.antiguedad-pill.antiguedad-critica { background: color-mix(in srgb, var(--color-error) 18%, transparent); color: var(--color-error); }

.mobile-list-wrap { padding: 0.75rem; }
.mobile-loader-wrap, .mobile-empty { padding: 1rem; text-align: center; }
.mobile-cards { display: flex; flex-direction: column; gap: 0.75rem; }
.mobile-card {
  border: 1px solid var(--color-border); background: var(--color-bg-light, transparent);
  border-radius: 14px; padding: 1rem; cursor: pointer; transition: border-color 0.15s;
}
.mobile-card:hover { border-color: var(--color-primary); }
.mobile-card-header { display: flex; justify-content: space-between; gap: 0.8rem; align-items: flex-start; margin-bottom: 0.75rem; }
.mobile-card-id { margin: 0; font-size: 0.78rem; color: var(--color-text); font-weight: 600; }
.mobile-card-cliente { margin: 0.2rem 0 0; font-weight: 700; color: var(--color-title); }
.mobile-card-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.6rem; }
.mobile-field-full { grid-column: 1 / -1; }
.mobile-label { display: block; font-size: 0.72rem; color: var(--color-text); margin-bottom: 0.15rem; text-transform: uppercase; }
.mobile-value { display: block; font-size: 0.88rem; color: var(--color-text); }

@media (max-width: 768px) {
  .fact-container { margin: 1rem auto; padding: 1rem 0.75rem; }
  .fact-toolbar { border-radius: 12px; }
}
</style>
