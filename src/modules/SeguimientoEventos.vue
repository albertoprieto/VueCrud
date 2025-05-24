<template>
  <div class="seguimiento-eventos">
    <h2 class="seguimiento-title">Seguimiento de Eventos</h2>

    <!-- Filtros -->
    <div class="filters">
      <Dropdown 
        v-model="selectedTechnician" 
        :options="['Todos', ...technicians]" 
        placeholder="Filtrar por Técnico" 
        class="filter-dropdown"
      />
    </div>

    <div class="seguimiento-card">
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
    </div>

    <Dialog v-model:visible="showReporteDialog" header="Detalle del Reporte" :closable="true" :modal="true">
      <div class="dialog-content" v-if="detalleReporte">
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
const selectedTechnician = ref('Todos');

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
  if (!selectedTechnician.value || selectedTechnician.value === 'Todos') {
    return events.value;
  }
  return events.value.filter(event => event.technician === selectedTechnician.value);
});
</script>

<style scoped>
.seguimiento-eventos {
  max-width: 900px;
  margin: 2rem auto;
  text-align: center;
  background: var(--color-bg);
  color: var(--color-text);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  padding: 2rem 1.5rem;
}
.seguimiento-title {
  margin-bottom: 2rem;
  color: var(--color-title); /* rosa opaco llamativo */
}
.filters {
  margin-bottom: 1rem;
  display: flex;
  justify-content: flex-end;
}
.filter-dropdown {
  min-width: 220px;
}
.seguimiento-card {
  background: var(--color-card);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 2rem;
}
.dialog-content {
  padding: 1rem 0.5rem;
  text-align: left;
}
@media (max-width: 700px) {
  .seguimiento-eventos {
    padding: 1rem 0.2rem;
  }
  .seguimiento-card {
    padding: 0.5rem;
  }
}
</style>