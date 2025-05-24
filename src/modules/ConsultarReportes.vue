<template>
  <div class="consultar-reportes-container">
    <h2 class="consultar-reportes-title">Consultar Reportes</h2>
    <DataTable :value="reportes" responsiveLayout="scroll">
      <Column field="modelo" header="Modelo" />
      <Column field="placa" header="Placa" />
      <Column field="cliente" header="Cliente" />
      <Column field="fecha" header="Fecha" />
    </DataTable>
  </div>
</template>

<script setup>
import { useReportesStore } from '@/stores/reportesStore';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';

const reportesStore = useReportesStore();
const reportes = reportesStore.getReportes();
</script>

<style scoped>
.consultar-reportes-container {
  max-width: 800px;
  margin: 2rem auto;
  text-align: center;
  background: #23272f;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  color: #e4c8c8;
  padding: 2rem 1.5rem;
}
.consultar-reportes-title {
  margin-bottom: 2rem;
  color: #e4c8c8;
}
</style>