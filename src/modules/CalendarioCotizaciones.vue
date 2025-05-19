<template>
  <div class="calendario-cotizaciones">
    <h2>Calendario de Cotizaciones</h2>

    <!-- Filtro por Técnico -->
    <!-- <div class="filters">
      <Dropdown 
        v-model="selectedTechnician" 
        :options="technicians" 
        placeholder="Filtrar por Técnico" 
        class="filter-dropdown"
      />
    </div> -->

    <FullCalendar :options="calendarOptions" />
    <div v-if="events.length === 0" class="no-events">
      <p>No hay eventos agendados.</p>
    </div>

    <!-- Modal para mostrar detalles del evento -->
    <Dialog v-model:visible="showDialog" header="Detalles del Evento" :closable="true" :modal="true">
      <p><strong>Título:</strong> {{ selectedEvent?.title }}</p>
      <p><strong>Fecha:</strong> {{ selectedEvent?.start }}</p>
      <p><strong>Descripción:</strong> {{ selectedEvent?.descripcion }}</p>
      <p><strong>IMEI:</strong> {{ selectedEvent?.imei }}</p>
      <p><strong>Técnico:</strong> {{ selectedEvent?.technician }}</p>
      <p><strong>Estado:</strong> {{ selectedEvent?.status }}</p>
      <Button 
        v-if="selectedEvent?.status === 'Agendado'" 
        label="Marcar como Realizado" 
        icon="pi pi-check" 
        class="p-button-success" 
        @click="openReportDialog"
      />
      <Button label="Cerrar" icon="pi pi-times" @click="closeDialog" />
    </Dialog>

    <Dialog v-model:visible="messageDialog" header="Éxito" :closable="false" :modal="true">
      <p>{{ messageText }}</p>
      <Button label="Aceptar" icon="pi pi-check" @click="messageDialog = false" />
    </Dialog>

    <Dialog v-model:visible="showReportDialog" header="Generar Reporte de Servicio" :closable="false" :modal="true">
      <div>
        <div class="form-group">
          <label>Modelo del Vehículo:</label>
          <InputText v-model="reportData.modelo" type="text" />
        </div>
        <div class="form-group">
          <label>Placa del Vehículo:</label>
          <InputText v-model="reportData.placa" type="text" />
        </div>
        <div class="form-group">
          <label>Observaciones:</label>
          <Textarea v-model="reportData.observaciones" rows="3" autoResize />
        </div>
        <Button label="Guardar y Concluir" icon="pi pi-check" @click="saveReportAndComplete" />
        <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary" @click="showReportDialog = false" />
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { getEventos, updateEventoStatus } from '@/services/eventosService';
import { addReporte } from '@/services/reportesService'; // Debes crear este servicio
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';

const technicians = ref(['Técnico 1', 'Técnico 2', 'Técnico 3']);
const selectedTechnician = ref(null);

const events = ref([]);
const showDialog = ref(false);
const selectedEvent = ref(null);

const calendarOptions = ref({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  locale: 'es',
  events: [],
  editable: true,
  eventClick: (info) => {
    selectedEvent.value = {
      id: info.event.id,
      descripcion: info.event.extendedProps.descripcion,
      imei: info.event.extendedProps.imei,
      technician: info.event.extendedProps.technician,
      status: info.event.extendedProps.status,
      title: info.event.title,
      start: info.event.startStr
    };
    showDialog.value = true;
  }
});

const loadEventos = async () => {
  const data = await getEventos();
  events.value = data;
  calendarOptions.value = {
    ...calendarOptions.value,
    events: data.map(event => ({
      id: event.id,
      title: event.title,
      start: event.start,
      extendedProps: {
        descripcion: event.descripcion,
        imei: event.imei,
        technician: event.technician,
        status: event.status
      },
      backgroundColor: event.status === 'Concluido' ? '#6c757d' :
                       event.status === 'En Proceso' ? '#007bff' :
                       event.status === 'Agendado' ? '#28a745' : '#ffcc00',
      borderColor: event.status === 'Concluido' ? '#6c757d' :
                   event.status === 'En Proceso' ? '#007bff' :
                   event.status === 'Agendado' ? '#28a745' : '#ffcc00'
    }))
  };
};

onMounted(loadEventos);

watch(selectedTechnician, async (newTech) => {
  if (!newTech) {
    await loadEventos();
  } else {
    const data = await getEventos();
    events.value = data.filter(e => e.technician === newTech);
    calendarOptions.value = {
      ...calendarOptions.value,
      events: events.value.map(event => ({
        id: event.id,
        title: event.title,
        start: event.start,
        extendedProps: {
          descripcion: event.descripcion,
          imei: event.imei,
          technician: event.technician,
          status: event.status
        },
        backgroundColor: event.status === 'Concluido' ? '#6c757d' :
                         event.status === 'En Proceso' ? '#007bff' :
                         event.status === 'Agendado' ? '#28a745' : '#ffcc00',
        borderColor: event.status === 'Concluido' ? '#6c757d' :
                     event.status === 'En Proceso' ? '#007bff' :
                     event.status === 'Agendado' ? '#28a745' : '#ffcc00'
      }))
    };
  }
});

const closeDialog = () => {
  showDialog.value = false;
  selectedEvent.value = null;
};

const messageDialog = ref(false);
const messageText = ref('');

const showReportDialog = ref(false);
const reportData = ref({
  modelo: '',
  placa: '',
  cliente: '',
  observaciones: ''
});
const pendingEventId = ref(null);

const openReportDialog = () => {
  reportData.value = {
    modelo: '',
    placa: '',
    cliente: selectedEvent.value?.cliente || '',
    observaciones: ''
  };
  pendingEventId.value = selectedEvent.value.id;
  showReportDialog.value = true;
};

const saveReportAndComplete = async () => {
  if (!reportData.value.placa || !reportData.value.observaciones) {
    messageText.value = 'Por favor, complete todos los campos.';
    messageDialog.value = true;
    return;
  }
  await addReporte({
    imei: selectedEvent.value.imei,
    cotizacion: selectedEvent.value.title,
    technician: selectedEvent.value.technician,
    start: selectedEvent.value.start,
    status: selectedEvent.value.status,
    modelo: reportData.value.modelo,
    placa: reportData.value.placa,
    cliente: reportData.value.cliente,
    observaciones: reportData.value.observaciones,
    eventoId: pendingEventId.value
  });
  await updateEventoStatus(pendingEventId.value, 'Concluido');
  await loadEventos();
  showReportDialog.value = false;
  messageText.value = 'Evento marcado como realizado y reporte generado correctamente.';
  messageDialog.value = true;
  closeDialog();
};

const markAsCompleted = () => {
  openReportDialog();
};
</script>

<style scoped>
.calendario-cotizaciones {
  max-width: 900px;
  margin: 0 auto;
}

.no-events {
  text-align: center;
  margin-top: 20px;
  font-size: 1.2rem;
  color: #666;
}

.filters {
  margin-bottom: 1rem;
  display: flex;
  justify-content: center;
}

.filter-dropdown {
  width: 300px;
}

.dialog {
  text-align: left;
}
</style>