<template>
  <div class="consultar">
    <h2>Consultar IMEIs Registrados</h2>
    <DataTable :value="items" responsiveLayout="scroll">
      <Column field="imei" header="IMEI" />
      <Column field="registeredBy" header="Registrado Por" />
      <Column field="date" header="Fecha de Registro" />
      <Column field="status" header="Estado" />
      <Column field="technician" header="Técnico">
        <template #body="slotProps">
          {{ slotProps.data.technician || 'NA' }}
        </template>
      </Column>
      <Column field="gpsModel" header="Modelo GPS">
        <template #body="slotProps">
          {{ slotProps.data.gpsModel || 'NA' }}
        </template>
      </Column>
      <Column header="Acciones">
        <template #body="slotProps">
          <Button label="Editar" icon="pi pi-pencil" class="p-button-text" @click="openEditModal(slotProps.data)" />
        </template>
      </Column>
    </DataTable>

    <Dialog v-model:visible="showEditDialog" header="Editar IMEI" :closable="true" :modal="true">
      <div v-if="editItem">
        <div class="form-group">
          <label>Técnico:</label>
          <Dropdown v-model="editItem.technician" :options="technicians" placeholder="Seleccionar técnico" />
        </div>
        <div class="form-group">
          <label>Modelo GPS:</label>
          <InputText v-model="editItem.gpsModel" placeholder="Modelo GPS" />
        </div>
        <div class="modal-actions">
          <Button label="Guardar" icon="pi pi-save" @click="saveEdit" />
          <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary" @click="closeEditModal" />
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { getIMEIs, updateIMEI } from '@/services/imeiService';

const items = ref([]);
const technicians = ref(['Juan', 'Pedro', 'Paco']);

const showEditDialog = ref(false);
const editItem = ref(null);

onMounted(async () => {
  items.value = await getIMEIs();
});

const openEditModal = (item) => {
  // Clonar para evitar edición directa hasta guardar
  editItem.value = { ...item };
  showEditDialog.value = true;
};

const closeEditModal = () => {
  showEditDialog.value = false;
  editItem.value = null;
};

const saveEdit = async () => {
  await updateIMEI(editItem.value.imei, editItem.value);
  // Actualizar la tabla localmente
  const idx = items.value.findIndex(i => i.imei === editItem.value.imei);
  if (idx !== -1) {
    items.value[idx] = { ...editItem.value };
  }
  closeEditModal();
};
</script>

<style scoped>
.consultar {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}
.form-group {
  margin-bottom: 1rem;
  text-align: left;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
</style>