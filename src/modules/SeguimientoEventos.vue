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
      <Column field="titulo" header="Título" />
      <Column field="descripcion" header="Descripción" />
      <Column field="fecha" header="Fecha" />
      <Column field="technician" header="Técnico" />
      <Column field="status" header="Estado" :body="statusTemplate" />
    </DataTable>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useEventosStore } from '@/stores/eventosStore';
import Dropdown from 'primevue/dropdown';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';

const eventosStore = useEventosStore();

// Lista de técnicos para el filtro
const technicians = ref(['Técnico 1', 'Técnico 2', 'Técnico 3']);
const selectedTechnician = ref(null);

// Obtener eventos desde el store
const events = computed(() => eventosStore.getEventos);

// Filtrar eventos por técnico seleccionado
const filteredEvents = computed(() => {
  if (!selectedTechnician.value) {
    return events.value;
  }
  return events.value.filter(event => event.technician === selectedTechnician.value);
});

// Plantilla para mostrar el estado con colores
const statusTemplate = (rowData) => {
  const statusColors = {
    Pendiente: '#ffcc00',
    Agendado: '#28a745',
    'En Proceso': '#007bff',
    Concluido: '#6c757d'
  };
  return `<span style="color: ${statusColors[rowData.status]}; font-weight: bold;">${rowData.status}</span>`;
};
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