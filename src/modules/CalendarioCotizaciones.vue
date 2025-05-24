<template>
  <div class="calendario-cotizaciones">
    <h2 class="calendario-title">Calendario de Cotizaciones</h2>

    <div class="calendario-card">
      <FullCalendar :options="calendarOptions" />
      <div v-if="events.length === 0" class="no-events">
        <p>No hay eventos agendados.</p>
      </div>
    </div>

    <!-- Modal para mostrar detalles del evento -->
    <Dialog v-model:visible="showDialog" header="Detalles del Servicio" :closable="true" :modal="true">
      <div class="dialog-content">
        <p><strong>Título:</strong> {{ selectedEvent?.descripcion }}</p>
        <p><strong>Fecha:</strong> {{ selectedEvent?.start ? selectedEvent.start.split('T')[0] : '' }}</p>
        <p><strong>Descripción:</strong> {{ selectedEvent?.descripcion }}</p>
        <p><strong>Cliente:</strong> {{ selectedEvent?.cliente }}</p>
        <p><strong>Estado:</strong> {{ selectedEvent?.status }}</p>
        <Button
          v-if="selectedEvent?.status === 'Agendado'"
          label="Realizar Reporte"
          icon="pi pi-check"
          class="p-button-success"
          @click="openReportDialog"
        />
        <Button class="ml-2" severity="danger" label="Cerrar" icon="pi pi-times" @click="closeDialog" />
      </div>
    </Dialog>

    <Dialog v-model:visible="messageDialog" header="Éxito" :closable="false" :modal="true">
      <div class="dialog-content">
        <p>{{ messageText }}</p>
        <Button label="Aceptar" icon="pi pi-check" @click="messageDialog = false" />
      </div>
    </Dialog>

    <Dialog v-model:visible="showReportDialog" header="Generar Reporte de Servicio" :closable="false" :modal="true">
      <div class="dialog-content">
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
        <div class="form-group">
          <label>Medio de Pago:</label>
          <Dropdown
            v-model="reportData.medio_pago"
            :options="['Efectivo', 'Transferencia', 'Depósito']"
            placeholder="Seleccione el medio de pago"
          />
        </div>
        <div class="form-group form-group-row">
          <Checkbox v-model="reportData.pagado" :binary="true" inputId="pagado" />
          <label for="pagado" style="margin-left: 0.5rem;">¿Pagado?</label>
        </div>
        <div class="dialog-actions">
          <Button label="Guardar y Concluir" icon="pi pi-check" @click="saveReportAndComplete" />
          <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary" @click="showReportDialog = false" />
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { getEventos, updateEventoStatus } from '@/services/eventosService';
import { addReporte } from '@/services/reportesService';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Checkbox from 'primevue/checkbox';

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
      cliente: info.event.extendedProps.cliente,
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
      title: event.technician,
      start: event.start,
      extendedProps: {
        descripcion: event.descripcion,
        imei: event.imei,
        cliente: event.title,
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
  observaciones: '',
  medio_pago: null,
  pagado: false
});
const pendingEventId = ref(null);

const openReportDialog = () => {
  reportData.value = {
    modelo: '',
    placa: '',
    cliente: selectedEvent.value?.cliente || '',
    observaciones: '',
    medio_pago: null,
    pagado: false
  };
  pendingEventId.value = selectedEvent.value.id;
  showReportDialog.value = true;
};

const saveReportAndComplete = async () => {
  if (!reportData.value.placa || !reportData.value.observaciones || !reportData.value.medio_pago) {
    messageText.value = 'Por favor, complete todos los campos.';
    messageDialog.value = true;
    return;
  }
  await addReporte({
    imei: selectedEvent.value.imei,
    cotizacion: selectedEvent.value.title,
    technician: selectedEvent.value.technician,
    start: selectedEvent.value.start,
    status: "Concluido",
    modelo: reportData.value.modelo,
    placa: reportData.value.placa,
    cliente: reportData.value.cliente,
    observaciones: reportData.value.observaciones,
    eventoId: pendingEventId.value,
    medio_pago: reportData.value.medio_pago,
    pagado: reportData.value.pagado
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
  margin: .5rem auto;
  text-align: center;
  background: var(--color-bg);
  color: var(--color-text);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  padding: 2rem 1.5rem;
}
.calendario-title {
  margin-bottom: .3rem;
  color: var(--color-title); /* rosa opaco llamativo */
}
.calendario-card {
  background: var(--color-card);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 2rem;
}
.no-events {
  text-align: center;
  margin-top: 20px;
  font-size: 1.2rem;
  color: #666;
}
.dialog-content {
  padding: 1rem 0.5rem;
  text-align: left;
}
.form-group {
  margin-bottom: 1.2rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.form-group-row {
  flex-direction: row !important;
  align-items: center !important;
}
.form-group label {
  font-weight: bold;
  margin-bottom: 0.4rem;
  color: var(--color-title); /* rosa opaco llamativo */
}
.p-inputtext,
.p-inputtextarea {
  width: 100%;
  box-sizing: border-box;
}
.dialog-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  justify-content: flex-end;
}
@media (max-width: 700px) {
  .calendario-cotizaciones {
    padding: 1rem 0.2rem;
  }
  .calendario-card {
    padding: 0.5rem;
  }
  .dialog-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>