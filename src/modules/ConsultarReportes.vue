<template>
  <div class="consultar-reportes">
    <h2>Consultar Reportes</h2>
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
.consultar-reportes {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}
</style>