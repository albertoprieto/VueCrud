<template>
  <div class="calendario-cotizaciones">
    <h2>Calendario de Cotizaciones</h2>
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
        @click="markAsCompleted" 
      />
      <Button label="Cerrar" icon="pi pi-times" @click="closeDialog" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useEventosStore } from '@/stores/eventosStore';
import { useQuotationStore } from '@/stores/quotationStore';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';

const eventosStore = useEventosStore();
const quotationStore = useQuotationStore();

// Computed property para obtener los eventos desde el store
const events = computed(() => {
  const eventos = eventosStore.getEventos();
  return eventos.map((evento) => ({
    title: evento.titulo,
    start: evento.fecha,
    descripcion: evento.descripcion,
    imei: evento.imei,
    technician: evento.technician,
    status: evento.status,
    backgroundColor: evento.status === 'Concluido' ? '#007bff' : evento.status === 'Agendado' ? '#28a745' : '#ffcc00',
    borderColor: evento.status === 'Concluido' ? '#007bff' : evento.status === 'Agendado' ? '#28a745' : '#ffcc00'
  }));
});

// Estado para el modal
const showDialog = ref(false);
const selectedEvent = ref(null);

// Opciones del calendario
const calendarOptions = ref({
  plugins: [dayGridPlugin],
  initialView: 'dayGridMonth',
  locale: 'es',
  events: events.value,
  editable: true, // Permitir arrastrar y soltar
  eventClick: (info) => {
    selectedEvent.value = {
      title: info.event.title,
      start: info.event.start.toISOString().split('T')[0],
      descripcion: info.event.extendedProps.descripcion,
      imei: info.event.extendedProps.imei,
      technician: info.event.extendedProps.technician,
      status: info.event.extendedProps.status
    };
    showDialog.value = true;
  },
  eventMouseEnter: (info) => {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.innerHTML = `
      <strong>${info.event.title}</strong><br>
      Fecha: ${info.event.start.toISOString().split('T')[0]}<br>
      Técnico: ${info.event.extendedProps.technician}
    `;
    document.body.appendChild(tooltip);
  }
});

// Watch para actualizar los eventos dinámicamente
watch(events, (newEvents) => {
  calendarOptions.value = {
    ...calendarOptions.value,
    events: newEvents
  };
});

// Función para marcar el evento como "Realizado"
const markAsCompleted = () => {
  if (selectedEvent.value) {
    // Actualizar el estado del evento en el store de eventos
    eventosStore.updateEvento({
      ...selectedEvent.value,
      status: 'Concluido'
    });

    // Actualizar el estado de la cotización en el store de cotizaciones
    const quotation = quotationStore.getQuotations().find(q => q.descripcion === selectedEvent.value.descripcion);
    if (quotation) {
      quotation.status = 'Concluido';
      quotationStore.updateQuotation(quotation);
    }

    // Cerrar el modal
    showDialog.value = false;
    selectedEvent.value = null;
  }
};

const closeDialog = () => {
  showDialog.value = false;
};

// Cargar datos al montar el componente
onMounted(() => {
  console.log('Eventos cargados:', events.value); // Depuración: Verifica los eventos procesados
});
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
</style>