<template>
  <div class="buscar-imei-container">
    <h2 class="buscar-imei-title">Buscar IMEI</h2>
    <div class="buscar-imei-filtros">
      <InputText
        v-model="filtro"
        placeholder="Filtra por últimos dígitos, artículo o ubicación..."
        class="buscar-imei-input"
      />
      <Button label="Limpiar" icon="pi pi-times" @click="filtro = ''" class="ml-2" />
    </div>
    <DataTable
      :value="imeisFiltrados"
      :paginator="true"
      :rows="10"
      responsiveLayout="scroll"
      class="buscar-imei-table"
      :loading="cargando"
      stripedRows
      :rowsPerPageOptions="[10, 20, 50]"
      emptyMessage="No se encontraron IMEIs."
    >
      <Column field="imei" header="IMEI" sortable />
      <Column field="articulo_nombre" header="Artículo" sortable />
      <Column field="sku" header="SKU" sortable />
      <Column field="ubicacion" header="Ubicación" sortable />
      <Column field="status" header="Estado">
        <template #body="slotProps">
          <span
            :class="{
              'imei-disponible': slotProps.data.status === 'Disponible',
              'imei-vendido': slotProps.data.status === 'Vendido',
              'imei-devuelto': slotProps.data.status === 'Devuelto'
            }"
          >
            {{ slotProps.data.status }}
          </span>
        </template>
      </Column>
      <Column header="Acciones">
        <template #body="slotProps">
          <Button
            v-if="slotProps.data.status === 'Vendido'"
            label="Devolver"
            icon="pi pi-undo"
            class="p-button-text p-button-warning"
            @click="devolver(slotProps.data.imei)"
          />
          <Button
            label="Transferir"
            icon="pi pi-exchange"
            class="p-button-text p-button-info ml-2"
            @click="transferir(slotProps.data.imei)"
          />
          <Button
            label="Eliminar"
            icon="pi pi-trash"
            class="p-button-text p-button-danger ml-2"
            @click="eliminar(slotProps.data.imei)"
          />
        </template>
      </Column>
    </DataTable>

    <Dialog v-model:visible="showConfirmDelete" header="Confirmar Eliminación" :modal="true" :closable="false">
      <div style="padding:1.5rem; text-align:center;">
        <span>¿Seguro que deseas eliminar este IMEI?</span>
      </div>
      <div class="modal-actions">
        <Button label="Eliminar" icon="pi pi-trash" class="p-button-danger" @click="eliminarConfirmado" />
        <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary ml-2" @click="showConfirmDelete = false" />
      </div>
    </Dialog>

    <Dialog v-model:visible="showTransferDialog" header="Transferir IMEI" :modal="true" :closable="false">
      <div style="padding:1.5rem; text-align:center;">
        <span>Selecciona la ubicación destino para transferir el IMEI:</span>
        <Dropdown
          v-model="ubicacionDestino"
          :options="ubicaciones"
          optionLabel="nombre"
          placeholder="Selecciona ubicación"
          class="w-full mt-3"
        />
      </div>
      <div class="modal-actions">
        <Button label="Transferir" icon="pi pi-exchange" class="p-button-info" @click="transferirConfirmado" :disabled="!ubicacionDestino" />
        <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary ml-2" @click="showTransferDialog = false" />
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Dropdown from 'primevue/dropdown';
import Column from 'primevue/column';
import Dialog from 'primevue/dialog';
import axios from 'axios';
import { devolverIMEI, deleteIMEI } from '@/services/imeiService';
import { getUbicaciones, asignarImeisUbicacion } from '@/services/ubicacionesService';
import { useToast } from 'primevue/usetoast';

const toast = useToast();

const imeis = ref([]);
const filtro = ref('');
const cargando = ref(false);

const showConfirmDelete = ref(false);
const imeiAEliminar = ref(null);

const showTransferDialog = ref(false);
const imeiATransferir = ref(null);
const ubicaciones = ref([]);
const ubicacionDestino = ref(null);

const cargarImeis = async () => {
  cargando.value = true;
  const res = await axios.get('https://api.gpsubicacionapi.com/buscar-imei?digitos=');
  imeis.value = res.data;
  cargando.value = false;
};

const cargarUbicaciones = async () => {
  ubicaciones.value = await getUbicaciones();
};

onMounted(async () => {
  await cargarImeis();
  await cargarUbicaciones();
});

const imeisFiltrados = computed(() => {
  if (!filtro.value) return imeis.value;
  const f = filtro.value.toLowerCase();
  return imeis.value.filter(i =>
    i.imei?.toLowerCase().includes(f) ||
    i.imei?.slice(-5).includes(f) ||
    i.articulo_nombre?.toLowerCase().includes(f) ||
    i.ubicacion?.toLowerCase().includes(f)
  );
});

const devolver = async (imei) => {
  try {
    await devolverIMEI(imei);
    await cargarImeis();
    toast.add({ severity: 'success', summary: 'IMEI devuelto', detail: 'El IMEI fue devuelto correctamente.', life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo devolver el IMEI.', life: 4000 });
  }
};

const eliminar = (imei) => {
  imeiAEliminar.value = imei;
  showConfirmDelete.value = true;
};

const eliminarConfirmado = async () => {
  if (!imeiAEliminar.value) return;
  try {
    await deleteIMEI(imeiAEliminar.value);
    await cargarImeis();
    toast.add({ severity: 'success', summary: 'IMEI eliminado', detail: 'El IMEI fue eliminado correctamente.', life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar el IMEI.', life: 4000 });
  }
  showConfirmDelete.value = false;
  imeiAEliminar.value = null;
};

const transferir = (imei) => {
  imeiATransferir.value = imei;
  ubicacionDestino.value = null;
  showTransferDialog.value = true;
};

const transferirConfirmado = async () => {
  if (!imeiATransferir.value || !ubicacionDestino.value) return;
  try {
    await asignarImeisUbicacion(ubicacionDestino.value.id, [imeiATransferir.value]);
    await cargarImeis();
    toast.add({ severity: 'success', summary: 'IMEI transferido', detail: 'El IMEI fue transferido correctamente.', life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo transferir el IMEI.', life: 4000 });
  }
  showTransferDialog.value = false;
  imeiATransferir.value = null;
  ubicacionDestino.value = null;
};
</script>

<style scoped>
.buscar-imei-container {
  max-width: 900px;
  margin: 2rem auto;
  background: var(--color-bg, #23272f);
  color: var(--color-text, #fff);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  padding: 2rem 1.5rem;
}
.buscar-imei-title {
  margin-bottom: 1.5rem;
  color: var(--color-title, #ff4081);
  text-align: center;
}
.buscar-imei-filtros {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}
.buscar-imei-input {
  flex: 1;
}
.buscar-imei-table {
  margin-top: 1rem;
}
.imei-devuelto {
  background: #ffe082;
  color: #795548;
  font-weight: bold;
}
</style>