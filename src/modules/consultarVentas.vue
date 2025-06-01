<template>
  <div class="consultar-ventas">
    <h2>Consultar Notas de Venta</h2>
    <div class="filtros">
      <InputText v-model="filtroCliente" placeholder="Filtrar por cliente..." class="mb-2" />
      <Button label="Buscar" icon="pi pi-search" @click="buscar" class="mb-2" />
    </div>
    <DataTable :value="ventasFiltradas">
      <Column field="id" header="ID" />
      <Column field="cliente_nombre" header="Cliente" />
      <Column field="fecha" header="Fecha">
        <template #body="slotProps">
          {{ formatFecha(slotProps.data.fecha) }}
        </template>
      </Column>
      <Column field="total" header="Total">
        <template #body="slotProps">
          {{ formatoMoneda(slotProps.data.total) }}
        </template>
      </Column>
      <Column header="Acciones">
        <template #body="slotProps">
          <Button label="Editar" icon="pi pi-pencil" class="p-button-text" @click="editar(slotProps.data)" />
          <Button label="Ver Detalle" icon="pi pi-eye" class="p-button-text" @click="verDetalle(slotProps.data)" />
        </template>
      </Column>
    </DataTable>
    <Dialog v-model:visible="showDetalle" header="Detalle de Venta" :modal="true">
      <div v-if="detalleVenta && detalleVenta.length" class="detalle-venta-dialog">
        <div class="mb-2">
          <strong>Fecha de nota:</strong>
          {{ formatFecha(ventaDetalle?.fecha) || 'Sin fecha' }}
        </div>
        <table class="detalle-table">
          <thead>
            <tr>
              <th>Artículo</th>
              <th>Cantidad</th>
              <th>Precio</th>
              <th>Subtotal</th>
              <th v-if="detalleVenta.some(i => i.imei)">IMEI</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in detalleVenta" :key="item.id">
              <td>{{ item.articulo_nombre }}</td>
              <td>{{ item.cantidad }}</td>
              <td>{{ formatoMoneda(item.precio_unitario) }}</td>
              <td>{{ formatoMoneda(item.cantidad * item.precio_unitario) }}</td>
              <td v-if="item.imei">{{ item.imei }}</td>
            </tr>
          </tbody>
        </table>
        <div class="detalle-venta-footer">
          <div><strong>Observaciones:</strong> {{ ventaDetalle?.observaciones || 'Sin observaciones' }}</div>
          <div class="detalle-total">
            <strong>Total:</strong>
            {{ formatoMoneda(detalleVenta.reduce((acc, item) => acc + (item.cantidad * item.precio_unitario), 0)) }}
          </div>
        </div>
      </div>
      <div v-else>
        <span>No hay detalle disponible.</span>
      </div>
      <Button label="Cerrar" @click="showDetalle.value = false" class="detalle-cerrar-btn" />
    </Dialog>
    <EditarVenta
      v-if="ventaEditando"
      :venta="ventaEditando"
      @cerrar="handleCerrarEditar"
      :key="ventaEditando ? ventaEditando.id + '-' + reloadKey : 'empty'"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useVentas } from '@/composables/useVentas.js';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import EditarVenta from './EditarVenta.vue';

const { ventas, cargarDetalleVenta, detalleVenta } = useVentas();
const filtroCliente = ref('');
const showDetalle = ref(false);
const ventaDetalle = ref(null);
const ventaEditando = ref(null);
const reloadKey = ref('');

const ventasFiltradas = computed(() =>
  filtroCliente.value
    ? ventas.value.filter(v => v.cliente_nombre?.toLowerCase().includes(filtroCliente.value.toLowerCase()))
    : ventas.value
);

function formatoMoneda(valor) {
  return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(Number(valor) || 0);
}

function formatFecha(fecha) {
  if (!fecha) return '';
  // Si ya está en formato YYYY-MM-DD, regresa igual
  if (/^\d{4}-\d{2}-\d{2}$/.test(fecha)) return fecha;
  // Si viene con hora o con 'T', corta solo la fecha
  if (typeof fecha === 'string' && (fecha.includes(' ') || fecha.includes('T')))
    return fecha.split(/[ T]/)[0];
  // Si es Date, formatea
  if (fecha instanceof Date) return fecha.toISOString().slice(0, 10);
  return fecha;
}

async function verDetalle(venta) {
  ventaDetalle.value = venta;
  await cargarDetalleVenta({ data: venta });
  showDetalle.value = true;
}
async function editar(venta) {
  await cargarDetalleVenta({ data: venta });
  ventaEditando.value = { ...venta, detalle: detalleVenta.value ? JSON.parse(JSON.stringify(detalleVenta.value)) : [] };
  reloadKey.value = venta.fecha ? venta.fecha.split(/[ T]/)[0] : '';
}
function buscar() {}
function handleCerrarEditar() {
  ventaEditando.value = null;
  reloadKey.value = '';
}
</script>

<style scoped>
.consultar-ventas {
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
}

.filtros {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.detalle-venta-dialog {
  min-width: 300px;
}

.detalle-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

.detalle-table th,
.detalle-table td {
  border: 1px solid #ddd;
  padding: 0.5rem;
  text-align: left;
}

.detalle-venta-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.detalle-total {
  font-weight: bold;
}

.detalle-cerrar-btn {
  margin-top: 1rem;
}
</style>