<template>
  <div class="consultar-cotizaciones">
    <h2>Consultar Cotizaciones</h2>
    <DataTable :value="quotations" responsiveLayout="scroll">
      <Column field="cliente" header="Cliente" />
      <Column field="descripcion" header="Descripción" />
      <Column field="monto" header="Monto" />
      <Column field="date" header="Fecha" />
      <Column field="status" header="Estado" />
      <Column header="Técnico Asignado">
        <template #body="slotProps">
          {{ slotProps.data.technician ? slotProps.data.technician : 'NA' }}
        </template>
      </Column>
      <Column header="IMEI Asignado">
        <template #body="slotProps">
          {{ slotProps.data.imei ? slotProps.data.imei : 'NA' }}
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

    <!-- Modal para asignar técnico -->
    <Dialog v-model:visible="showAssignDialog" header="Asignar Técnico e IMEI" :closable="true" :modal="true" aria-labelledby="assign-modal-title">
      <div class="modal-content">
        <h3 id="assign-modal-title">Asignar Técnico e IMEI</h3>
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
        
        <div class="form-group">
          <label for="imei">Asignar IMEI:</label>
          <Dropdown id="imei" v-model="selectedIMEI" :options="imeis" option-label="imei" placeholder="Seleccione un IMEI" />
          <small v-if="!selectedIMEI" class="error-text">Este campo es obligatorio.</small>
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
import { getIMEIs, updateIMEI } from '@/services/imeiService';
import { addEvento } from '@/services/eventosService';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Calendar from 'primevue/calendar';
import Dropdown from 'primevue/dropdown';

const quotations = ref([]);
const imeis = ref([]);
const technicians = ref(['Juan', 'Pedro', 'Paco']);

const showAssignDialog = ref(false);
const selectedQuotation = ref(null);
const calendarDate = ref(null);
const selectedTechnician = ref(null);
const selectedIMEI = ref(null);

const showMessageDialog = ref(false);
const messageDialogText = ref('');

onMounted(async () => {
  quotations.value = await getQuotations();
  const imeiList = await getIMEIs();
  imeis.value = imeiList.filter(item => item.status === 'Disponible');
});

const openAssignDialog = (quotation) => {
  selectedQuotation.value = quotation;
  calendarDate.value = quotation.calendarDate || null;
  selectedTechnician.value = quotation.technician || null;
  selectedIMEI.value = imeis.value.find(item => item.imei === quotation.imei) || null;
  showAssignDialog.value = true;
};

const assignDetails = async () => {
  if (!calendarDate.value || !selectedTechnician.value || !selectedIMEI.value) {
    messageDialogText.value = 'Por favor, complete todos los campos.';
    showMessageDialog.value = true;
    return;
  }

  try {
    await updateQuotation(selectedQuotation.value.id, {
      ...selectedQuotation.value,
      technician: selectedTechnician.value,
      imei: selectedIMEI.value.imei,
      calendarDate: calendarDate.value,
      status: 'Agendado'
    });
    await addEvento({
      title: `Servicio para ${selectedQuotation.value.cliente}`,
      descripcion: selectedQuotation.value.descripcion,
      cliente: selectedQuotation.value.cliente,
      imei: selectedIMEI.value.imei,
      technician: selectedTechnician.value,
      start: calendarDate.value,
      status: 'Agendado'
    });
    await updateIMEI(selectedIMEI.value.imei, {
      ...selectedIMEI.value,
      status: 'Asignado'
    });
    messageDialogText.value = 'Detalles asignados exitosamente.';
    // Refresca la lista de cotizaciones
    quotations.value = await getQuotations();
  } catch (error) {
    messageDialogText.value = 'Error al actualizar la cotización.';
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
  selectedIMEI.value = null;
};
</script>

<style scoped>
.consultar-cotizaciones {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.text-center {
  text-align: center;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.error-text {
  color: red;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}
</style>