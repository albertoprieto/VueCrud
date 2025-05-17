<template>
  <div class="consultar-cotizaciones">
    <h2>Consultar Cotizaciones</h2>
    <DataTable :value="quotations" responsiveLayout="scroll">
      <Column field="cliente" header="Cliente" />
      <Column field="descripcion" header="Descripción" />
      <Column field="monto" header="Monto" />
      <Column field="date" header="Fecha" />
      <Column header="Acciones" body-class="text-center">
        <template #body="slotProps">
          <Button 
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
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useQuotationStore } from '@/stores/quotationStore';
import { useItemsStore } from '@/stores/itemStore';
import { useEventosStore } from '@/stores/eventosStore';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Calendar from 'primevue/calendar';
import Dropdown from 'primevue/dropdown';

const quotationStore = useQuotationStore();
const itemsStore = useItemsStore();
const eventosStore = useEventosStore();

const quotations = quotationStore.getQuotations();
const showAssignDialog = ref(false);
const selectedQuotation = ref(null);
const calendarDate = ref(null);
const selectedTechnician = ref(null);
const selectedIMEI = ref(null);

const technicians = ref(['Técnico 1', 'Técnico 2', 'Técnico 3']);

const imeis = ref(itemsStore.items.filter(item => item.status === 'Disponible')); // Solo IMEIs disponibles

const openAssignDialog = (quotation) => {
  selectedQuotation.value = quotation;
  calendarDate.value = quotation.calendarDate || null;
  selectedTechnician.value = quotation.technician || null;
  selectedIMEI.value = imeis.value.find(item => item.imei === quotation.imei) || null;
  showAssignDialog.value = true;
};

const assignDetails = () => {
  if (!calendarDate.value || !selectedTechnician.value || !selectedIMEI.value) {
    alert('Por favor, complete todos los campos.');
    return;
  }

  // Actualizar la cotización
  selectedQuotation.value.status = 'Agendado';
  selectedQuotation.value.calendarDate = calendarDate.value;
  selectedQuotation.value.technician = selectedTechnician.value;
  selectedQuotation.value.imei = selectedIMEI.value.imei;

  quotationStore.updateQuotation(selectedQuotation.value);

  // Registrar el evento en el calendario
  eventosStore.addEvento({
    titulo: `Servicio para ${selectedQuotation.value.cliente}`,
    fecha: calendarDate.value,
    descripcion: selectedQuotation.value.descripcion,
    imei: selectedIMEI.value.imei,
    technician: selectedTechnician.value,
    status: 'Agendado'
  });

  // Actualizar el estado del IMEI
  const imeiToUpdate = itemsStore.items.find(item => item.imei === selectedIMEI.value.imei);
  if (imeiToUpdate) {
    imeiToUpdate.status = 'Asignado';
    itemsStore.updateItem(imeiToUpdate);
  }

  alert('Detalles asignados exitosamente.');
  closeDialog();
};

const closeDialog = () => {
  showAssignDialog.value = false;
  resetModalFields();
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