<template>
  <div class="seguimiento-eventos">
    <h2>Seguimiento de Eventos</h2>

    <!-- Filtros -->
    <div class="filters">
      <Dropdown 
        v-model="selectedTechnician" 
        :options="technicians" 
        placeholder="Filtrar por Técnico" 
        class="filter-dropdown"
      />
    </div>

    <!-- Tabla de Eventos -->
    <DataTable :value="filteredEvents" responsiveLayout="scroll">
      <Column field="title" header="Título" />
      <Column field="descripcion" header="Descripción Cotización" />
      <Column field="cliente" header="Cliente">
        <template #body="slotProps">
          {{ slotProps.data.cliente || 'NA' }}
        </template>
      </Column>
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
    </DataTable>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useEventosStore } from '@/stores/eventosStore';
import Dropdown from 'primevue/dropdown';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';

const eventosStore = useEventosStore();

const technicians = ref(['Técnico 1', 'Técnico 2', 'Técnico 3']);
const selectedTechnician = ref(null);

const statusColors = {
  Pendiente: '#ffcc00',
  Agendado: '#28a745',
  'En Proceso': '#007bff',
  Concluido: '#6c757d'
};

const events = computed(() => eventosStore.getEventos);

onMounted(() => {
  console.log('Eventos en seguimiento:', events.value);
});

watch(events, (newEvents) => {
  console.log('Eventos actualizados en seguimiento:', newEvents);
});

// Filtrar eventos por técnico seleccionado
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