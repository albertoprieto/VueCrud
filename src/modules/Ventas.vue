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
            {{ getStockDisponible(slotProps.data.articulo_id, slotProps.data) }}
          </template>
        </Column>
        <Column field="cantidad" header="Cantidad">
          <template #body="slotProps">
            <InputText
              type="number"
              v-model.number="slotProps.data.cantidad"
              :min="1"
              :max="mostrarColumnaIMEI(slotProps.data.articulo_id) ? 1 : getStockDisponible(slotProps.data.articulo_id, slotProps.data)"
              class="w-full"
              :disabled="!slotProps.data.articulo_id || mostrarColumnaIMEI(slotProps.data.articulo_id)"
              @input="validateCantidad(slotProps.data)"
            />
            <small v-if="slotProps.data.cantidad > getStockDisponible(slotProps.data.articulo_id, slotProps.data)" class="error-text">
              Máx: {{ getStockDisponible(slotProps.data.articulo_id, slotProps.data) }}
            </small>
            <small v-if="mostrarColumnaIMEI(slotProps.data.articulo_id)" class="info-text">
              Solo puedes vender un equipo por fila si requiere IMEI.
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
              <Dropdown
                v-if="mostrarColumnaIMEI(slotProps.data.articulo_id)"
                v-model="slotProps.data.imei"
                :options="imeisDisponiblesPorArticulo(slotProps.data.articulo_id, slotProps.data)"
                optionLabel="imei"
                optionValue="imei"
                placeholder="Selecciona IMEI"
                class="w-full imei-dropdown"
                :disabled="!slotProps.data.articulo_id"
              />
              <div v-if="slotProps.data.imei" class="imei-seleccionado">
                <span>IMEI seleccionado:</span>
                <span class="imei-value">{{ slotProps.data.imei }}</span>
              </div>
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
        <Textarea v-model="venta.observaciones" rows="2" />
      </div>

      <div class="mb-2">
        <strong>Total: ${{ totalVenta.toFixed(2) }}</strong>
      </div>

      <Button label="Guardar Venta" class="mb-2" @click="guardarVenta" :disabled="!venta.cliente_id || venta.articulos.length === 0" />

      <h2 class="ventas-title">Ventas Registradas</h2>
      <DataTable :value="ventas" selectionMode="single" v-model:selection="ventaSeleccionada" @rowSelect="cargarDetalleVenta">
        <Column field="id" header="ID" />
        <Column field="cliente_nombre" header="Cliente" />
        <Column field="fecha" header="Fecha" />
        <Column field="total" header="Total" />
      </DataTable>

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
}
.ventas-dialog :deep(.p-dialog-header) {
  background: var(--color-bg);
  color: var(--color-title);
  border-bottom: 1px solid #e0e0e0;
  border-radius: 12px 12px 0 0;
  font-size: 1.2rem;
  font-weight: bold;
  padding: 1rem 1.5rem;
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