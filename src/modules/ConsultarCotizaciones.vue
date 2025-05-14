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
            label="Ver Detalles" 
            icon="pi pi-eye" 
            class="p-button-text" 
            @click="viewDetails(slotProps.data)" 
          />
          <Button 
            label="Asignar a Técnico" 
            icon="pi pi-calendar" 
            class="p-button-text" 
            @click="openCalendarDialog(slotProps.data)" 
          />
        </template>
      </Column>
    </DataTable>

    <!-- Modal para detalles -->
    <Dialog v-model:visible="showDialog" header="Detalles de la Cotización" :closable="true" :modal="true">
      <p><strong>Cliente:</strong> {{ selectedQuotation?.cliente }}</p>
      <p><strong>Descripción:</strong> {{ selectedQuotation?.descripcion }}</p>
      <p><strong>Monto:</strong> {{ selectedQuotation?.monto }}</p>
      <p><strong>Fecha:</strong> {{ selectedQuotation?.date }}</p>
      <Button label="Cerrar" icon="pi pi-times" @click="closeDialog" />
    </Dialog>

    <!-- Modal para calendarizar -->
    <Dialog v-model:visible="showCalendarDialog" header="Calendarizar Cotización" :closable="true" :modal="true">
      <p><strong>Cliente:</strong> {{ selectedQuotation?.cliente }}</p>
      <p><strong>Descripción:</strong> {{ selectedQuotation?.descripcion }}</p>
      <div class="form-group">
        <label for="fecha">Fecha de la Cita:</label>
        <Calendar v-model="calendarDate" placeholder="Seleccione una fecha" />
      </div>
      <div class="form-group">
        <label for="tecnico">Asignar Técnico:</label>
        <Dropdown v-model="selectedTechnician" :options="technicians" placeholder="Seleccione un técnico" />
      </div>
      <Button label="Guardar" icon="pi pi-save" @click="scheduleQuotation" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useQuotationStore } from '@/stores/quotationStore';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Calendar from 'primevue/calendar';
import Dropdown from 'primevue/dropdown';

const quotationStore = useQuotationStore();
const quotations = quotationStore.getQuotations();
const showDialog = ref(false);
const showCalendarDialog = ref(false);
const selectedQuotation = ref(null);
const calendarDate = ref(null);
const selectedTechnician = ref(null);
const technicians = ref([
  { label: 'Técnico 1', value: 'Técnico 1' },
  { label: 'Técnico 2', value: 'Técnico 2' },
  { label: 'Técnico 3', value: 'Técnico 3' }
]);

const viewDetails = (quotation) => {
  selectedQuotation.value = quotation;
  showDialog.value = true;
};

const openCalendarDialog = (quotation) => {
  selectedQuotation.value = quotation;
  showCalendarDialog.value = true;
};

const closeDialog = () => {
  showDialog.value = false;
  selectedQuotation.value = null;
};

const scheduleQuotation = () => {
  if (!calendarDate.value || !selectedTechnician.value) {
    alert('Por favor, seleccione una fecha y un técnico.');
    return;
  }

  // Actualizar el estado de la cotización
  selectedQuotation.value.status = 'Agendado';
  selectedQuotation.value.calendarDate = calendarDate.value;
  selectedQuotation.value.technician = selectedTechnician.value;

  quotationStore.updateQuotation(selectedQuotation.value);

  alert('Cotización calendarizada exitosamente.');
  showCalendarDialog.value = false;
  selectedQuotation.value = null;
  calendarDate.value = null;
  selectedTechnician.value = null;
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
</style>