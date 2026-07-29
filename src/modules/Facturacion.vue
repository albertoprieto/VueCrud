<template>
  <div class="fact-container">
    <h2 class="fact-title"><i class="pi pi-receipt" /> Facturación</h2>

    <!-- Lo que hay que ver rápido: qué falta timbrar. -->
    <div class="banner-pendientes" :class="{ 'sin-pendientes': !pendientesTimbre.length }">
      <i :class="pendientesTimbre.length ? 'pi pi-exclamation-triangle' : 'pi pi-check-circle'" />
      <span v-if="pendientesTimbre.length">
        <strong>{{ pendientesTimbre.length }}</strong> prefactura{{ pendientesTimbre.length === 1 ? '' : 's' }} pendiente{{ pendientesTimbre.length === 1 ? '' : 's' }} de timbrar
        por <strong>{{ formatTotal(totalPendienteTimbre) }}</strong>.
      </span>
      <span v-else>No hay prefacturas pendientes de timbrar.</span>
    </div>

    <div class="fact-filtros">
      <InputText v-model="filtroCliente" placeholder="Buscar por cliente..." class="filtro-cliente" />
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
      <Column header="Total">
        <template #body="{ data }">{{ formatTotal(data.total) }}</template>
      </Column>
      <Column header="Estatus">
        <template #body="{ data }">
          <span :class="'badge badge-' + badgeClass(data.status)">{{ data.status }}</span>
        </template>
      </Column>
      <Column header="Fecha">
        <template #body="{ data }">{{ formatFecha(data.fecha) }}</template>
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
          </div>
        </article>
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
import { getFacturas, eliminarFactura } from '@/services/pagosService';

const router = useRouter();
const toast = useToast();

const facturas = ref([]);
const loading = ref(true);
const isMobile = ref(false);
const filtroCliente = ref('');
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

const facturasFiltradas = computed(() => {
  const cl = filtroCliente.value.trim().toLowerCase();
  return facturas.value.filter(f => {
    if (filtroEstado.value !== 'todos' && f.status !== filtroEstado.value) return false;
    if (cl && !(f.cliente || '').toLowerCase().includes(cl)) return false;
    return true;
  });
});

const pendientesTimbre = computed(() => facturas.value.filter(f => f.status === 'Pendiente timbre'));
const totalPendienteTimbre = computed(() => pendientesTimbre.value.reduce((acc, f) => acc + (Number(f.total) || 0), 0));

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

onMounted(() => {
  setViewportMode();
  window.addEventListener('resize', setViewportMode);
  cargar();
});
onBeforeUnmount(() => window.removeEventListener('resize', setViewportMode));
</script>

<style scoped>
.fact-container { margin: 2rem auto; padding: 2rem 1.5rem; max-width: 1300px; }
.fact-title { display:flex; align-items:center; justify-content:center; gap:0.5rem; color: var(--color-title); margin-bottom: 1.5rem; }
.banner-pendientes {
  display: flex; align-items: center; justify-content: center; gap: 0.6rem;
  padding: 0.85rem 1.25rem; margin-bottom: 1.5rem; border-radius: 12px;
  font-size: 0.92rem; font-weight: 600;
  background: color-mix(in srgb, var(--color-warning) 16%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-warning) 40%, transparent);
  color: var(--color-warning);
}
.banner-pendientes.sin-pendientes {
  background: color-mix(in srgb, var(--color-success) 14%, transparent);
  border-color: color-mix(in srgb, var(--color-success) 40%, transparent);
  color: var(--color-success);
}
.fact-filtros { display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; margin-bottom: 1.5rem; }
.filtro-cliente { flex: 1; min-width: 220px; }
.filtro-estado { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.estado-chip {
  display: flex; align-items: center; gap: 0.35rem;
  padding: 0.4rem 0.9rem; border-radius: 999px;
  border: 1px solid var(--color-border); background: var(--color-card); color: var(--color-text);
  cursor: pointer; font-size: 0.85rem; font-weight: 600;
}
.estado-chip.activo { background: var(--color-primary); border-color: var(--color-primary); color: var(--color-on-primary, #fff); }
.estado-chip-count { opacity: 0.7; font-weight: 700; }
.badge { padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.85rem; font-weight: bold; }
.badge-success { background: color-mix(in srgb, var(--color-success) 22%, transparent); color: var(--color-success); }
.badge-warning { background: color-mix(in srgb, var(--color-warning) 25%, transparent); color: var(--color-warning); }
.badge-danger  { background: color-mix(in srgb, var(--color-error) 20%, transparent); color: var(--color-error); }

.mobile-list-wrap { margin-top: 0.5rem; }
.mobile-loader-wrap, .mobile-empty { background: var(--color-card); border: 1px solid var(--color-border); border-radius: 12px; padding: 1rem; text-align: center; }
.mobile-cards { display: flex; flex-direction: column; gap: 0.75rem; }
.mobile-card { border: 1px solid var(--color-border); background: var(--color-card); border-radius: 12px; padding: 0.9rem; cursor: pointer; }
.mobile-card-header { display: flex; justify-content: space-between; gap: 0.8rem; align-items: flex-start; margin-bottom: 0.75rem; }
.mobile-card-id { margin: 0; font-size: 0.78rem; color: var(--color-text); font-weight: 600; }
.mobile-card-cliente { margin: 0.2rem 0 0; font-weight: 700; color: var(--color-title); }
.mobile-card-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.6rem; }
.mobile-label { display: block; font-size: 0.72rem; color: var(--color-text); margin-bottom: 0.15rem; text-transform: uppercase; }
.mobile-value { display: block; font-size: 0.88rem; color: var(--color-text); }

@media (max-width: 768px) {
  .fact-container { margin: 1rem auto; padding: 1rem 0.75rem; }
}
</style>
