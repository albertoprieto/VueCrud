<template>
  <div class="calendario-asignaciones">
    <h2>Calendario de Asignaciones a Técnicos</h2>
    <FullCalendar :options="calendarOptions" />
    <Dialog v-model:visible="showDialog" header="Resumen de Asignación" :modal="true">
      <div v-if="asignacionSeleccionada">
        <p><b>Técnico:</b> {{ asignacionSeleccionada.tecnico }}</p>
        <p><b>Fecha de servicio:</b> {{ asignacionSeleccionada.fecha_servicio }}</p>
        <p><b>Nota de venta:</b> {{ asignacionSeleccionada.venta_id }}</p>
        <p v-if="asignacionSeleccionada.cliente_id"><b>Cliente:</b> {{ asignacionSeleccionada.cliente_id }}</p>
      </div>
      <template #footer>
        <Button label="Ver Detalle" icon="pi pi-search" @click="verDetalle" />
        <Button label="Cerrar" icon="pi pi-times" class="p-button-secondary" @click="showDialog = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import { getAsignacionesTecnicos } from '@/services/asignacionesService';

const asignaciones = ref([]);
const showDialog = ref(false);
const asignacionSeleccionada = ref(null);
const router = useRouter();

const calendarOptions = ref({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  locale: 'es',
  events: [],
  eventClick: (info) => {
    asignacionSeleccionada.value = info.event.extendedProps;
    showDialog.value = true;
  }
});

onMounted(async () => {
  asignaciones.value = await getAsignacionesTecnicos();
  const eventos = asignaciones.value
    .filter(a => !!a.fecha_servicio)
    .map(a => ({
      id: a.id,
      title: `Técnico: ${a.tecnico} - Venta: ${a.venta_id}`,
      start: a.fecha_servicio,
      extendedProps: a
    }));
  calendarOptions.value = {
    ...calendarOptions.value,
    events: eventos
  };
});

function verDetalle() {
  showDialog.value = false;
  router.push(`/asignacion/${asignacionSeleccionada.value.id}`);
}
</script>

<style scoped>
.calendario-asignaciones {
  max-width: 900px;
  margin: 2rem auto;
  background: var(--color-bg);
  color: var(--color-text);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  padding: 2rem 1.5rem;
}
</style>