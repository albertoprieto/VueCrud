<template>
  <div class="calendar-container">
    <FullCalendar
      :options="calendarOptions"
    />
    <Dialog v-model:visible="showDialog" :header="dialogTitle" :modal="true" :closable="true" :style="{ width: '400px' }">
      <div v-if="selectedEvent">
        <div class="dialog-section">
          <strong>Técnico:</strong> {{ selectedEvent.extendedProps?.tecnico || '-' }}
        </div>
        <div class="dialog-section">
          <strong>Cliente:</strong> {{ selectedEvent.extendedProps?.cliente || selectedEvent.extendedProps?.cliente_id || '-' }}
        </div>
        <div class="dialog-section">
          <strong>Nota de Venta:</strong> {{ selectedEvent.extendedProps?.venta_folio || selectedEvent.extendedProps?.venta_id || '-' }}
        </div>
        <div class="dialog-section">
          <strong>Fecha de Servicio:</strong> {{ selectedEvent.startStr?.slice(0,10) || '-' }}
        </div>
        <div class="dialog-section">
          <strong>Detalle:</strong> {{ selectedEvent.extendedProps?.descripcion || 'Sin descripción' }}
        </div>
        <div class="dialog-actions">
          <Button label="Agregar Reporte" icon="pi pi-plus" class="p-button-success mr-2 p-button-sm" @click="irReporteServicio(selectedEventData)" />
          <Button label="Descargar Orden" icon="pi pi-file-pdf" class="p-button-secondary p-button-sm" @click="descargarNota(selectedEventData)" v-if="selectedEventData.venta_id" />
        </div>
      </div>
    </Dialog>
    <EditarVenta
      v-if="showEditarVenta && ventaAEditar"
      :venta="ventaAEditar"
      :clientes="clientes"
      @cerrar="cerrarEditarVenta"
      @guardar="guardarEditarVenta"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { useRouter } from 'vue-router';
import { getAsignacionesTecnicos } from '@/services/asignacionesService';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import { getVentas, getDetalleVenta } from '@/services/ventasService';
import { getClientes } from '@/services/clientesService';
import { getTodosArticulos } from '@/services/articulosService';
import { generarNotaVentaPDF } from '@/services/NotaVentaPdfService.js';
import EditarVenta from '@/modules/EditarVenta.vue';
import esLocale from '@fullcalendar/core/locales/es';

const events = ref([]);
const showDialog = ref(false);
const selectedEvent = ref(null);
const dialogTitle = ref('Detalle de Asignación');
const router = useRouter();
const selectedEventData = ref({});
const showEditarVenta = ref(false);
const ventaAEditar = ref(null);
const clientes = ref([]);

onMounted(async () => {
  const asignaciones = await getAsignacionesTecnicos();
  events.value = asignaciones.map(a => ({
    title: a.tecnico ? `Técnico: ${a.tecnico}` : 'Asignación',
    start: a.fecha_servicio,
    description: `Cliente: ${a.cliente || a.cliente_id || ''}\nVenta: ${a.venta_folio || a.venta_id || ''}`,

    ...a
  }));
  calendarOptions.value.events = events.value;
});

function handleEventClick(info) {
  selectedEvent.value = info.event;
  dialogTitle.value = info.event.title;
  selectedEventData.value = info.event.extendedProps;
  showDialog.value = true;
}

function irDetalleDirecto(asignacion) {
  router.push(`/asignacion/${asignacion.id}`);
}
function irReporteServicio(asignacion) {
  router.push(`/reporte-servicio/${asignacion.id}`);
}
async function descargarNota(asignacion) {
  if (!asignacion.venta_id) return;
  const [ventas, clientes, articulos, detalle] = await Promise.all([
    getVentas(),
    getClientes(),
    getTodosArticulos(),
    getDetalleVenta(asignacion.venta_id)
  ]);
  const venta = ventas.find(v => v.id === asignacion.venta_id);
  const cliente = clientes.find(c => c.id === venta.cliente_id) || {};
  const articulosSeleccionados = detalle.map(item => {
    const art = articulos.find(a => a.id === item.articulo_id) || {};
    return {
      ...item,
      sku: art.sku,
      nombre: art.nombre
    };
  });
  await generarNotaVentaPDF({
    venta,
    cliente,
    articulos: articulosSeleccionados,
    empresa: {
      nombre: 'GPSubicacion.com',
      direccion: 'Guadalajara',
      rfc: 'RFC123456'
    }
  });
}

const calendarOptions = ref({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay',
  },
  events: events.value,
  eventClick: handleEventClick,
  height: 'auto',
  locale: esLocale, // <-- Aquí va el objeto importado
  selectable: true,
  editable: false,
});
</script>

<style scoped>
.calendar-container {
  max-width: 900px;
  margin: 2rem auto;
  border-radius: 1rem;
  padding: 1rem;
}

/* Elimina estilos de .fc que afectan DataTable y otros componentes globales */
/* .fc {
  --fc-today-bg-color: var(--color-today, #e3f2fd);
  --fc-event-bg-color: var(--color-primary, #1976d2);
  --fc-event-border-color: var(--color-primary, #1976d2);
  --fc-event-text-color: var(--color-on-primary, #fff);
} */

.dialog-section {
  margin-bottom: 0.5rem;
}
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
}
</style>
