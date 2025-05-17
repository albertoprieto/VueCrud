<template>
  <div class="calendario-cotizaciones">
    <h2>Calendario de Cotizaciones</h2>

    <!-- Filtro por Técnico -->
    <div class="filters">
      <Dropdown 
        v-model="selectedTechnician" 
        :options="technicians" 
        placeholder="Filtrar por Técnico" 
        class="filter-dropdown"
      />
    </div>

    <FullCalendar :options="calendarOptions" />
    <div v-if="events.length === 0" class="no-events">
      <p>No hay eventos agendados.</p>
    </div>

    <!-- Modal para mostrar detalles del evento -->
    <Dialog v-model:visible="showDialog" header="Detalles del Evento" :closable="true" :modal="true">
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
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';

const eventosStore = useEventosStore();

// Lista de técnicos para el filtro
const technicians = ref(['Técnico 1', 'Técnico 2', 'Técnico 3']);
const selectedTechnician = ref(null);

// Computed property para obtener los eventos desde el store
const events = computed(() => eventosStore.getEventos);

// Opciones del calendario
const calendarOptions = ref({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  locale: 'es',
  events: events.value,
  editable: true,
  eventClick: (info) => {
    console.log('Evento clicado:', info.event);
  }
});

// Watch para actualizar los eventos dinámicamente
watch(events, (newEvents) => {
  calendarOptions.value = {
    ...calendarOptions.value,
    events: newEvents.map(event => ({
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
});

// Depuración: Verifica los eventos cargados
onMounted(() => {
  console.log('Eventos en el calendario:', events.value);
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