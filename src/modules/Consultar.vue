<template>
  <div class="consultar">
    <h2 style="color:#debdc9;">Histórico IMEI</h2>
    <DataTable :value="filteredItems" responsiveLayout="scroll">
      <template #header>
        <div class="datatable-header">
          <span>Filtrar por técnico:</span>
          <Dropdown
            v-model="selectedTechnician"
            :options="['Todos', ...technicians]"
            placeholder="Selecciona técnico"
            class="datatable-dropdown"
          />
        </div>
      </template>
      <Column field="imei" header="IMEI" />
      <Column field="registeredBy" header="Registró" />
      <Column field="date" header="Fecha">
        <template #body="slotProps">
          {{ slotProps.data.date?.split(' ')[0] || '' }}
        </template>
      </Column>
      <Column field="status" header="Estado" />
      <Column field="technician" header="Técnico">
        <template #body="slotProps">
          {{ slotProps.data.technician || 'NA' }}
        </template>
      </Column>
      <Column field="gpsModel" header="Modelo">
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
import { ref, onMounted, computed } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { getIMEIs, updateIMEI } from '@/services/imeiService';

const items = ref([]);
const technicians = ref(['Juan', 'Pedro', 'Paco']);
const selectedTechnician = ref('Todos');

const filteredItems = computed(() => {
  if (!selectedTechnician.value || selectedTechnician.value === 'Todos') {
    return items.value;
  }
  return items.value.filter(i => i.technician === selectedTechnician.value);
});

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
  text-align: left;
  padding: 1rem;
}

.datatable-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-bottom: 0.5rem;
}

.datatable-dropdown {
  min-width: 180px;
}

@media (max-width: 600px) {
  .consultar {
    max-width: 100%;
    padding: 0.5rem;
  }
  .datatable-header {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  .datatable-dropdown {
    width: 100%;
  }
  .p-datatable .p-datatable-thead > tr > th,
  .p-datatable .p-datatable-tbody > tr > td {
    font-size: 0.85rem;
    padding: 0.5rem;
    white-space: nowrap;
  }
  .modal-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
</style>