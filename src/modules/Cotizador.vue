<template>
  <div class="cotizador-container">
    <h2 class="cotizador-title">Cotizador</h2>
    <div class="cotizador-card">
      <form @submit.prevent="guardarCotizacion">
        <!-- Cliente y fecha -->
        <div class="form-row">
          <div class="form-group">
            <label>Cliente</label>
            <Dropdown v-model="cotizacion.cliente_id" :options="clientes" optionLabel="nombre" optionValue="id" placeholder="Selecciona un cliente" class="w-full" />
          </div>
          <div class="form-group">
            <label>Fecha</label>
            <InputText v-model="cotizacion.fecha" type="date" class="w-full" />
          </div>
        </div>
        <!-- Artículos -->
        <h3>Artículos</h3>
        <DataTable :value="cotizacion.articulos" class="mb-2">
          <Column field="articulo_id" header="Artículo">
            <template #body="slotProps">
              <Dropdown
                v-model="slotProps.data.articulo_id"
                :options="articulosConStock(slotProps.data)"
                optionLabel="nombre"
                optionValue="id"
                placeholder="Selecciona artículo"
                class="w-full"
                @change="onArticuloChange(slotProps.data.articulo_id, slotProps.data)"
              />
            </template>
          </Column>
          <Column field="cantidad" header="Cantidad">
            <template #body="slotProps">
              <InputText
                type="number"
                v-model.number="slotProps.data.cantidad"
                min="1"
                class="w-full"
                @input="validateCantidad(slotProps.data)"
              />
            </template>
          </Column>
          <Column field="precio_unitario" header="Precio Unitario">
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
          <Column header="Acciones">
            <template #body="slotProps">
              <Button icon="pi pi-trash" class="p-button-danger p-button-sm" @click="removeArticulo(slotProps.index)" />
            </template>
          </Column>
        </DataTable>
        <Button label="Agregar Artículo" icon="pi pi-plus" class="mb-2" @click="addArticulo" />

        <!-- Observaciones y monto -->
        <div class="form-row">
          <div class="form-group">
            <label>Observaciones</label>
            <InputText v-model="cotizacion.observaciones" class="w-full" />
          </div>
          <div class="form-group">
            <label>Monto total</label>
            <InputText v-model="cotizacion.monto" class="w-full" disabled />
          </div>
        </div>

        <div class="actions-right">
          <Button label="Guardar Cotización" icon="pi pi-save" type="submit" />
        </div>
      </form>
      <Dialog v-model:visible="showDialog" header="Cotización Guardada" :closable="false" :modal="true">
        <p>La cotización ha sido guardada exitosamente.</p>
        <Button label="Aceptar" icon="pi pi-check" @click="closeDialog" />
      </Dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import { useVentas } from '@/composables/useVentas.js';
import { addQuotation } from '@/services/quotationService';
import { useToast } from 'primevue/usetoast';

const toast = useToast();
const showDialog = ref(false);

const {
  clientes,
  articulosConStock,
  onArticuloChange,
  validateCantidad,
  addArticulo,
  removeArticulo,
} = useVentas();

const cotizacion = ref({
  cliente_id: null,
  fecha: new Date().toISOString().slice(0, 10),
  observaciones: '',
  articulos: [],
  monto: 0,
  status: 'Pendiente'
});

const calcularMonto = () => {
  cotizacion.value.monto = cotizacion.value.articulos.reduce(
    (sum, a) => sum + (a.cantidad * a.precio_unitario), 0
  );
};

watch(
  () => cotizacion.value.articulos,
  calcularMonto,
  { deep: true }
);

const guardarCotizacion = async () => {
  if (!cotizacion.value.cliente_id || cotizacion.value.articulos.length === 0) {
    toast.add({ severity: 'warn', summary: 'Campos obligatorios', detail: 'Selecciona cliente y al menos un artículo.', life: 4000 });
    return;
  }
  try {
    await addQuotation({
      ...cotizacion.value,
      articulos: cotizacion.value.articulos,
      status: 'Pendiente'
    });
    showDialog.value = true;
    cotizacion.value = {
      cliente_id: null,
      fecha: new Date().toISOString().slice(0, 10),
      observaciones: '',
      articulos: [],
      monto: 0,
      status: 'Pendiente'
    };
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al registrar la cotización', life: 4000 });
  }
};

const closeDialog = () => {
  showDialog.value = false;
};
</script>

<style scoped>
.cotizador-container {
  max-width: 700px;
  margin: 2rem auto;
  padding: 2rem 1.5rem;
  background: var(--color-bg);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
}
.cotizador-title {
  margin-bottom: 2rem;
  color: var(--color-title, #ff4081);
  text-align: center;
  font-size: 2rem;
  font-weight: bold;
  letter-spacing: 1px;
}
.cotizador-card {
  background: var(--color-card, #23272f);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}
.form-group {
  flex: 1 1 220px;
  min-width: 220px;
  margin-bottom: 0.5rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: var(--color-title);
}
.w-full {
  width: 100%;
}
.actions-right {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
}
</style>