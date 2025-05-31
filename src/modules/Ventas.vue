<template>
  <div class="ventas-container">
    <h2 class="ventas-title">Registrar Nota de Venta</h2>
    <div class="ventas-card">
      <div class="ventas-form-header">
        <div class="ventas-form-col">
          <label class="mb-2">Cliente</label>
          <Dropdown v-model="venta.cliente_id" :options="clientes" optionLabel="nombre" optionValue="id" placeholder="Selecciona un cliente" class="w-full" />
        </div>
        <div class="ventas-form-col">
          <label>Fecha</label>
          <InputText v-model="venta.fecha" :value="today" readonly class="fecha-input" />
        </div>
      </div>

      <h3>Artículos</h3>
      <DataTable :value="venta.articulos" responsiveLayout="scroll" class="venta-articulos-table">
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
              :disabled="articulosConStock(slotProps.data).length === 0"
            />
          </template>
        </Column>
        <Column header="Stock">
          <template #body="slotProps">
            <span v-if="esServicio(slotProps.data.articulo_id)">NA</span>
            <span v-else>
              {{ getStockDisponible(slotProps.data.articulo_id, slotProps.data) }}
            </span>
          </template>
        </Column>
        <Column field="cantidad" header="Cantidad">
          <template #body="slotProps">
            <InputText
              type="number"
              v-model.number="slotProps.data.cantidad"
              :min="1"
              :max="!esServicio(slotProps.data.articulo_id) ? getStockDisponible(slotProps.data.articulo_id, slotProps.data) : null"
              class="w-full"
              :disabled="!slotProps.data.articulo_id"
              @input="validateCantidad(slotProps.data)"
            />
            <small v-if="!esServicio(slotProps.data.articulo_id) && slotProps.data.cantidad > getStockDisponible(slotProps.data.articulo_id, slotProps.data)" class="error-text">
              Máx: {{ getStockDisponible(slotProps.data.articulo_id, slotProps.data) }}
            </small>
          </template>
        </Column>
        <Column field="precio_unitario" header="Precio">
          <template #body="slotProps">
            <span>{{ slotProps.data.precio_unitario.toFixed(2) }}</span>
          </template>
        </Column>
        <Column field="subtotal" header="Subtotal">
          <template #body="slotProps">
            {{ (slotProps.data.cantidad * slotProps.data.precio_unitario).toFixed(2) }}
          </template>
        </Column>
        <Column header="Acciones">
          <template #body="slotProps">
            <Button icon="pi pi-trash" class="p-button-danger p-button-sm" @click="removeArticulo(slotProps.index)" />
          </template>
        </Column>
        <Column header="IMEI">
          <template #body="slotProps">
            <div class="imei-cell">
              <template v-if="esServicio(slotProps.data.articulo_id)">
                <span>NA</span>
              </template>
              <template v-else-if="mostrarColumnaIMEI(slotProps.data.articulo_id)">
                <div v-for="idx in slotProps.data.cantidad" :key="idx" style="margin-bottom: 0.2em;">
                  <Dropdown
                    v-model="slotProps.data.imeis[idx - 1]"
                    :options="imeisDisponiblesPorArticulo(slotProps.data.articulo_id, slotProps.data, idx - 1)"
                    optionLabel="imei"
                    optionValue="imei"
                    placeholder="Selecciona IMEI"
                    class="w-full imei-dropdown"
                    :disabled="!slotProps.data.articulo_id"
                    filter
                  />
                </div>
                <div v-if="slotProps.data.imeis && slotProps.data.imeis.length">
                  <span v-for="(imei, idx) in slotProps.data.imeis" :key="imei" class="imei-seleccionado" v-if="imei">
                    IMEI {{ idx + 1 }}: <span class="imei-value">{{ imei }}</span>
                  </span>
                </div>
              </template>
            </div>
          </template>
        </Column>
      </DataTable>
      <Button
        label="Agregar Artículo"
        icon="pi pi-plus"
        class="mb-2"
        @click="addArticulo"
        :disabled="articulosConStock().length === 0"
      />

      <div class="mb-2">
        <label>Observaciones</label>
        <InputText v-model="venta.observaciones" class="w-full" />
      </div>

      <div class="mb-2 acciones-footer">
        <strong>Total: ${{ totalVenta.toFixed(2) }}</strong>
        <Button
          label="Guardar Venta"
          class="mb-2"
          @click="guardarVentaConLoading"
          :disabled="!venta.cliente_id || venta.articulos.length === 0 || loadingGuardar"
        />
      </div>

      <Dialog v-model:visible="showDialog" header="Venta registrada" :closable="false" :modal="true" class="ventas-dialog">
        <p>La nota de venta se registró correctamente.</p>
        <Button label="Aceptar" icon="pi pi-check" @click="showDialog = false" autofocus />
      </Dialog>
    </div>
  </div>
</template>

<script setup>
import { useVentas } from '@/composables/useVentas.js';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Dialog from 'primevue/dialog';
import { ref } from 'vue';

const {
  today,
  clientes,
  articulosDisponibles,
  ventas,
  ventaSeleccionada,
  detalleVenta,
  imeis,
  showDialog,
  venta,
  totalVenta,
  articulosConStock,
  getStockDisponible,
  imeisDisponiblesPorArticulo,
  mostrarColumnaIMEI,
  addArticulo,
  removeArticulo,
  validateCantidad,
  onArticuloChange,
  guardarVenta,
  cargarDetalleVenta
} = useVentas();

const showDetalleDialog = ref(false);
const loadingGuardar = ref(false);

// Devuelve true si el artículo es de tipo Servicio
const esServicio = (articulo_id) => {
  const art = articulosDisponibles.value.find(a => a.id === articulo_id);
  return art && art.tipo && art.tipo.toLowerCase() === 'servicio';
};

async function guardarVentaConLoading() {
  console.log('Guardando venta:', venta);
  
  loadingGuardar.value = true;
  try {
    await guardarVenta();
  } finally {
    loadingGuardar.value = false;
  }
}
</script>

<style scoped>
.ventas-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
  background: var(--color-bg);
  color: var(--color-text);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
}
.ventas-title {
  margin-bottom: 2rem;
  color: var(--color-title);
  text-align: center;
}
.ventas-card {
  background: var(--color-card);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 2rem;
}
.ventas-form-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 1.5rem;
  gap: 1rem;
}
.ventas-form-col {
  flex: 1;
}
.mb-2 {
  margin-bottom: 1rem;
}
.w-full {
  width: 100%;
}
.venta-articulos-table {
  margin-bottom: 2rem;
  background: var(--color-card);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 1.5rem;
}
.imei-seleccionado {
  background: var(--color-bg-light);
  color: var(--color-primary);
  border-radius: 4px;
  padding: 0.15rem 0.5rem;
  margin-top: 0.15rem;
  font-size: 0.95em;
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
.error-text {
  color: var(--color-error);
  font-size: 0.85em;
  margin-top: 0.1rem;
  display: block;
}
.info-text {
  color: var(--color-primary);
  font-size: 0.85em;
  margin-top: 0.1rem;
  display: block;
}
.ventas-dialog :deep(.p-dialog-content) {
  background: var(--color-card);
  padding: 1.5rem 1rem;
  border-radius: 12px;
  color: var(--color-text);
}
.ventas-dialog :deep(.p-dialog-header) {
  background: var(--color-bg);
  color: var(--color-title);
  border-bottom: 1px solid var(--color-border);
  border-radius: 12px 12px 0 0;
  font-size: 1.2rem;
  font-weight: bold;
  padding: 1rem 1.5rem;
}
.detalle-venta-dialog {
  padding: 0.5rem 0;
}
.detalle-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
  background: var(--color-card);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  color: var(--color-text);
}
.detalle-table th, .detalle-table td {
  padding: 0.7em 1em;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}
.detalle-table th {
  background: var(--color-bg);
  color: var(--color-title);
  font-weight: 600;
}
.detalle-table tr:last-child td {
  border-bottom: none;
}
.detalle-venta-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  margin-top: 1rem;
  font-size: 1.05em;
  color: var(--color-text);
}
.detalle-total {
  color: var(--color-title);
  font-size: 1.15em;
  font-weight: bold;
}
.detalle-cerrar-btn {
  margin-top: 1.5rem;
  float: right;
}
.acciones-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 2rem;
  margin-bottom: 1rem;
}
.acciones-footer strong {
  font-size: 1.1em;
}
@media (max-width: 700px) {
  .ventas-container {
    padding: 1rem 0.2rem;
  }
  .ventas-card {
    padding: 0.5rem;
  }
  .ventas-form-header {
    flex-direction: column;
    gap: 0.5rem;
  }
  .venta-articulos-table {
    font-size: 0.95em;
    padding: 0.5rem;
  }
}
</style>