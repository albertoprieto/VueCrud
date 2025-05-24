<template>
  <div class="consultar-cotizaciones">
    <h2 class="consultar-cotizaciones-title">Consultar Cotizaciones</h2>
    <div class="consultar-cotizaciones-card">
      <DataTable :value="quotations" responsiveLayout="scroll">
        <Column field="cliente" header="Cliente" />
        <Column field="telefono" header="Teléfono" />
        <!-- <Column field="correo" header="Correo" /> -->
        <Column field="tipo" header="Tipo" />
        <Column field="modelo" header="Modelo GPS" />
        <Column field="descripcion" header="Descripción" />
        <!-- <Column field="observaciones" header="Observaciones" /> -->
        <Column field="monto" header="Monto" />
        <Column field="fecha" header="Fecha" />
        <Column field="status" header="Estado" />
        <Column header="Técnico Asignado">
          <template #body="slotProps">
            {{ slotProps.data.technician ? slotProps.data.technician : 'NA' }}
          </template>
        </Column>
        <Column header="Acciones" body-class="text-center">
          <template #body="slotProps">
            <Button
              v-if="slotProps.data.status === 'Agendado'"
              label="Editar"
              icon="pi pi-pencil"
              class="p-button-text"
              @click="openAssignDialog(slotProps.data)"
            />
            <Button
              v-else
              label="Asignar Técnico"
              icon="pi pi-calendar"
              class="p-button-text"
              @click="openAssignDialog(slotProps.data)"
            />
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Modal para asignar técnico -->
    <Dialog v-model:visible="showAssignDialog" header="Asignar Técnico" :closable="true" :modal="true" aria-labelledby="assign-modal-title">
      <div class="modal-content">
        <h3 id="assign-modal-title">Asignar Técnico</h3>
        <p><strong>Cliente:</strong> {{ selectedQuotation?.cliente }}</p>
        <p><strong>Descripción:</strong> {{ selectedQuotation?.descripcion }}</p>
        
        <div class="form-group">
          <label for="fecha">Fecha del Evento:</label>
          <Calendar id="fecha" v-model="calendarDate" placeholder="Seleccione una fecha" />
          <small v-if="!calendarDate" class="error-text">Este campo es obligatorio.</small>
        </div>
        
        <div class="form-group">
          <label for="tecnico">Asignar Técnico:</label>
          <Dropdown id="tecnico" v-model="selectedTechnician" :options="technicians" placeholder="Seleccione un técnico" />
          <small v-if="!selectedTechnician" class="error-text">Este campo es obligatorio.</small>
        </div>
        
        <div class="modal-actions">
          <Button label="Guardar" icon="pi pi-save" @click="assignDetails" />
          <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary" @click="closeDialog" />
        </div>
      </div>
    </Dialog>

    <!-- Dialog para mensajes -->
    <Dialog v-model:visible="showMessageDialog" header="Mensaje" :closable="false" :modal="true">
      <p>{{ messageDialogText }}</p>
      <Button label="Aceptar" icon="pi pi-check" @click="closeMessageDialog" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getQuotations, updateQuotation } from '@/services/quotationService';
import { addEvento } from '@/services/eventosService';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Calendar from 'primevue/calendar';
import Dropdown from 'primevue/dropdown';

const quotations = ref([]);
const technicians = ref(['Juan', 'Pedro', 'Paco']);

const showAssignDialog = ref(false);
const selectedQuotation = ref(null);
const calendarDate = ref(null);
const selectedTechnician = ref(null);

const showMessageDialog = ref(false);
const messageDialogText = ref('');

onMounted(async () => {
  quotations.value = await getQuotations();
});

const openAssignDialog = (quotation) => {
  selectedQuotation.value = quotation;
  calendarDate.value = quotation.calendarDate || null;
  selectedTechnician.value = quotation.technician || null;
  showAssignDialog.value = true;
};

const assignDetails = async () => {
  if (!calendarDate.value || !selectedTechnician.value) {
    messageDialogText.value = 'Por favor, complete todos los campos.';
    showMessageDialog.value = true;
    return;
  }

  try {
    await updateQuotation(selectedQuotation.value.id, {
      ...selectedQuotation.value,
      technician: selectedTechnician.value,
      calendarDate: calendarDate.value,
      status: 'Agendado'
    });
    await addEvento({
      title: `${selectedQuotation.value.cliente}`,
      descripcion: selectedQuotation.value.descripcion,
      cliente: selectedQuotation.value.cliente,
      technician: selectedTechnician.value,
      start: calendarDate.value,
      status: 'Agendado'
    });
    messageDialogText.value = 'Detalles asignados exitosamente.';
    quotations.value = await getQuotations();
  } catch (error) {
    console.error('Error en assignDetails:', error);
    messageDialogText.value = `Error al actualizar la cotización: ${error?.message || error}`;
  }
  showMessageDialog.value = true;
  closeDialog();
};

const closeDialog = () => {
  showAssignDialog.value = false;
  resetModalFields();
};

const closeMessageDialog = () => {
  showMessageDialog.value = false;
};

const resetModalFields = () => {
  selectedQuotation.value = null;
  calendarDate.value = null;
  selectedTechnician.value = null;
};
</script>

<style scoped>
.consultar-cotizaciones {
  max-width: 900px;
  margin: 2rem auto;
  text-align: center;
  background: var(--color-bg);
  color: var(--color-text);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  padding: 2rem 1.5rem;
}
.consultar-cotizaciones-title {
  margin-bottom: 2rem;
  color: var(--color-title); /* rosa opaco llamativo */
}
.consultar-cotizaciones-card {
  background: var(--color-card);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 2rem;
}
.text-center {
  text-align: center;
}
.form-group {
  margin-bottom: 1rem;
  text-align: left;
}
label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: var(--color-title); /* rosa opaco llamativo */
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}
.error-text {
  color: #d32f2f;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}
@media (max-width: 700px) {
  .consultar-cotizaciones {
    padding: 1rem 0.2rem;
  }
  .consultar-cotizaciones-card {
    padding: 0.5rem;
  }
  .modal-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>