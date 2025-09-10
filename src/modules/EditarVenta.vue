<template>
  <Dialog v-model:visible="visible" header="Editar Nota de Venta" :modal="true" class="ventas-dialog">
    <div class="ventas-form-header">
      <div class="ventas-form-col">
        <label class="mb-2">Cliente</label>
        <Dropdown v-model="ventaEdit.cliente_id" :options="clientes" optionLabel="nombre" optionValue="id" placeholder="Selecciona un cliente" class="w-full" disabled />
      </div>
      <div class="ventas-form-col">
        <label>Fecha</label>
        <InputText v-model="ventaEdit.fecha" type="date" class="fecha-input" />
      </div>
    </div>
    <div class="mb-2">
      <label>Observaciones</label>
      <InputText v-model="ventaEdit.observaciones" class="w-full" />
    </div>
    <h3>Artículos</h3>
    <DataTable :value="ventaEdit.detalle" responsiveLayout="scroll" class="venta-articulos-table">
      <Column header="Artículo">
        <template #body="slotProps">
          <Dropdown
            v-model="slotProps.data.articulo_id"
            :options="articulosConStock(slotProps.data)"
            optionLabel="nombre"
            optionValue="id"
            placeholder="Selecciona artículo"
            class="w-full"
            @change="onArticuloChange(slotProps.data.articulo_id, slotProps.data)"
            :disabled="true"
          />
        </template>
      </Column>
      <Column header="Cantidad">
        <template #body="slotProps">
          <InputText
            type="number"
            v-model.number="slotProps.data.cantidad"
            :min="1"
            :max="mostrarColumnaIMEI(slotProps.data.articulo_id) ? 1 : getStockDisponible(slotProps.data.articulo_id, slotProps.data)"
            class="w-full"
            :disabled="mostrarColumnaIMEI(slotProps.data.articulo_id)"
            @input="validateCantidad(slotProps.data)"
          />
        </template>
      </Column>
      <Column header="Precio">
        <template #body="slotProps">
          <InputText
            type="number"
            v-model.number="slotProps.data.precio_unitario"
            min="0"
            step="0.01"
            class="w-full"
          />
        </template>
      </Column>
      <Column header="IMEI">
        <template #body="slotProps">
          <Dropdown
            v-model="slotProps.data.imei"
            :options="[...(imeisDisponiblesPorArticulo(slotProps.data.articulo_id, slotProps.data) || []), ...(slotProps.data.imei ? [{ imei: slotProps.data.imei }] : [])]"
            optionLabel="imei"
            optionValue="imei"
            placeholder="Selecciona IMEI"
            class="w-full"
            :disabled="!slotProps.data.articulo_id"
          />
        </template>
      </Column>

    </DataTable>
    <div class="modal-actions">
      <Button label="Guardar" icon="pi pi-save" @click="guardar" />
      <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary" @click="cerrar" />
    </div>
  </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import { useVentas } from '@/composables/useVentas.js';

const props = defineProps({ venta: Object, clientes: Array });
const emit = defineEmits(['cerrar', 'guardar']);

const {
  articulosConStock,
  getStockDisponible,
  imeisDisponiblesPorArticulo,
  mostrarColumnaIMEI,
  validateCantidad,
  onArticuloChange,
} = useVentas();

const visible = ref(true);

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

const ventaEdit = ref({
  ...props.venta,
  fecha: formatFecha(props.venta.fecha),
  detalle: props.venta.detalle ? JSON.parse(JSON.stringify(props.venta.detalle)) : []
});

//
//

watch(() => props.venta, (nueva) => {
  //
  ventaEdit.value = {
    ...nueva,
    fecha: formatFecha(nueva.fecha),
    detalle: nueva.detalle ? JSON.parse(JSON.stringify(nueva.detalle)) : []
  };
  //
});

function guardar() {
  emit('guardar', { ...ventaEdit.value });
  cerrar();
}
function cerrar() {
  visible.value = false;
  emit('cerrar');
}
function eliminarArticulo(idx) {
  ventaEdit.value.detalle.splice(idx, 1);
}
</script>

<style scoped>
.ventas-dialog {
  width: 80vw;
  max-width: 900px;
}
.ventas-form-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}
.ventas-form-col {
  flex: 1;
}
.fecha-input {
  width: 100%;
}
.mb-2 {
  margin-bottom: 0.5rem;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}
.venta-articulos-table {
  width: 100%;
  margin-bottom: 1rem;
}
.venta-articulos-table .p-datatable-thead > tr > th {
  background-color: var(--color-bg);
  color: var(--color-title);
  font-weight: 600;
}
.venta-articulos-table .p-datatable-tbody > tr > td {
  border-bottom: 1px solid var(--color-border);
}
.venta-articulos-table .p-datatable-tbody > tr:last-child > td {
  border-bottom: none;
}
</style>