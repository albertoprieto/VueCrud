<template>
  <div class="pagos-container">
    <h2 class="pagos-title">Pagos — Histórico</h2>

    <!-- Tabs: Notas / Facturas -->
    <div class="pagos-tabs">
      <Button
        :class="['tab-btn', tab === 'notas' ? 'tab-active' : '']"
        label="Notas"
        icon="pi pi-file"
        @click="tab = 'notas'"
      />
      <Button
        :class="['tab-btn', tab === 'facturas' ? 'tab-active' : '']"
        label="Facturas"
        icon="pi pi-receipt"
        @click="tab = 'facturas'"
      />
    </div>

    <!-- ════════ NOTAS ════════ -->
    <div v-if="tab === 'notas'">
      <DataTable
        :value="notas"
        responsiveLayout="scroll"
        :loading="loadingNotas"
        :paginator="true"
        :rows="10"
        :rowsPerPageOptions="[5, 10, 20, 50]"
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
        <Column field="total" header="Total">
          <template #body="{ data }">
            {{ data.total != null ? '$' + Number(data.total).toFixed(2) : '-' }}
          </template>
        </Column>
        <Column field="status" header="Estatus">
          <template #body="{ data }">
            <span :class="'badge badge-' + badgeClassNota(data.status)">{{ data.status }}</span>
          </template>
        </Column>
        <Column field="fecha" header="Fecha">
          <template #body="{ data }">{{ formatFecha(data.fecha) }}</template>
        </Column>
        <Column header="Acciones" style="width: 220px">
          <template #body="{ data }">
            <div style="display: flex; gap: 0.5rem;">
              <Button icon="pi pi-eye" class="p-button-sm p-button-info" label="Detalle"
                @click="irDetalle('nota', data.id)" />
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
        :value="facturas"
        responsiveLayout="scroll"
        :loading="loadingFacturas"
        :paginator="true"
        :rows="10"
        :rowsPerPageOptions="[5, 10, 20, 50]"
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
        <Column field="total" header="Total">
          <template #body="{ data }">
            {{ data.total != null ? '$' + Number(data.total).toFixed(2) : '-' }}
          </template>
        </Column>
        <Column field="status" header="Estatus">
          <template #body="{ data }">
            <span :class="'badge badge-' + badgeClassFactura(data.status)">{{ data.status }}</span>
          </template>
        </Column>
        <Column field="fecha" header="Fecha">
          <template #body="{ data }">{{ formatFecha(data.fecha) }}</template>
        </Column>
        <Column header="Acciones" style="width: 220px">
          <template #body="{ data }">
            <div style="display: flex; gap: 0.5rem;">
              <Button icon="pi pi-eye" class="p-button-sm p-button-info" label="Detalle"
                @click="irDetalle('factura', data.id)" />
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
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import DataTableLoader from '@/components/DataTableLoader.vue';
import { getNotas, getFacturas, eliminarNota, eliminarFactura } from '@/services/pagosService';
import { useToast } from 'primevue/usetoast';

const router = useRouter();
const toast = useToast();

const tab = ref('notas');
const notas = ref([]);
const facturas = ref([]);
const loadingNotas = ref(false);
const loadingFacturas = ref(false);

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
  max-width: 1200px;
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
.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.85rem;
  font-weight: bold;
}
.badge-success { background: #c8e6c9; color: #256029; }
.badge-warning { background: #fff3cd; color: #856404; }
.badge-danger  { background: #f8d7da; color: #721c24; }
</style>
