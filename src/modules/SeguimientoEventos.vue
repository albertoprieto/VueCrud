<template>
  <div class="seguimiento-eventos">
    <h2 style="color:#debdc9;">Seguimiento de Eventos</h2>

    <!-- Filtros -->
    <!-- <div class="filters">
      <Dropdown 
        v-model="selectedTechnician" 
        :options="technicians" 
        placeholder="Filtrar por Técnico" 
        class="filter-dropdown"
      />
    </div> -->

    <!-- Tabla de Eventos -->
    <DataTable :value="filteredEvents" responsiveLayout="scroll">
      <Column field="title" header="Cliente" />
      <Column field="descripcion" header="Descripción Cotización" />
      <Column field="imei" header="IMEI" />
      <Column field="start" header="Fecha" />
      <Column field="technician" header="Técnico" />
      <Column field="status" header="Estado">
        <template #body="slotProps">
          <span :style="{ color: statusColors[slotProps.data.status], fontWeight: 'bold' }">
            {{ slotProps.data.status }}
          </span>
        </template>
      </Column>
      <Column header="Acciones">
        <template #body="slotProps">
          <Button
            v-if="slotProps.data.status === 'Concluido' && slotProps.data.reporte"
            label="Ver Detalle"
            icon="pi pi-eye"
            class="p-button-text"
            @click="verDetalleReporte(slotProps.data.reporte)"
          />
        </template>
      </Column>
    </DataTable>

    <Dialog v-model:visible="showReporteDialog" header="Detalle del Reporte" :closable="true" :modal="true">
      <div v-if="detalleReporte">
        <p><strong>Modelo:</strong> {{ detalleReporte.modelo }}</p>
        <p><strong>Placa:</strong> {{ detalleReporte.placa }}</p>
        <p><strong>Observaciones:</strong> {{ detalleReporte.observaciones }}</p>
        <p><strong>Fecha:</strong> {{ detalleReporte.start.split('T')[0] }}</p>
        <p><strong>Medio de Pago:</strong> {{ detalleReporte.medio_pago || 'NA' }}</p>
        <p><strong>¿Pagado?:</strong> {{ detalleReporte.pagado ? 'Sí' : 'No' }}</p>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { getEventos } from '@/services/eventosService';
import { getReportesByEvento } from '@/services/reportesService';
import Dropdown from 'primevue/dropdown';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';

const technicians = ref(['Técnico 1', 'Técnico 2', 'Técnico 3']);
const selectedTechnician = ref(null);

const statusColors = {
  Pendiente: '#ffcc00',
  Agendado: '#28a745',
  'En Proceso': '#007bff',
  Concluido: '#6c757d'
};

const events = ref([]);
const showReporteDialog = ref(false);
const detalleReporte = ref(null);

const loadEventos = async () => {
  const eventos = await getEventos();
  for (const evento of eventos) {
    if (evento.status === 'Concluido') {
      const reportes = await getReportesByEvento(evento.id);
      evento.reporte = reportes && reportes.length ? reportes[0] : null;
    } else {
      evento.reporte = null;
    }
  }
  events.value = eventos;
};

const verDetalleReporte = (reporte) => {
  detalleReporte.value = reporte;
  showReporteDialog.value = true;
};

onMounted(loadEventos);

watch(selectedTechnician, loadEventos);

const filteredEvents = computed(() => {
  if (!selectedTechnician.value) {
    return events.value;
  }
  return events.value.filter(event => event.technician === selectedTechnician.value);
});
</script>

<style scoped>
.seguimiento-eventos {
  max-width: 900px;
  margin: 0 auto;
  text-align: center;
}

.filters {
  margin-bottom: 1rem;
  display: flex;
  justify-content: center;
}

.filter-dropdown {
  width: 300px;
}

.data-table {
  margin-top: 1rem;
}
</style>