<template>
  <div class="consultar-reportes-container">
    <h2 class="consultar-reportes-title">Consultar Reportes de Servicio</h2>
    <DataTable :value="reportes" responsiveLayout="scroll" :loading="loading">
      <Column field="id" header="ID" />
      <Column field="asignacion_id" header="Asignación" />
      <Column field="tipo_servicio" header="Tipo de Servicio" />
      <Column field="marca" header="Marca" />
      <Column field="modelo" header="Modelo" />
      <Column field="placas" header="Placas" />
      <Column field="nombre_cliente" header="Cliente" />
      <Column field="fecha" header="Fecha" />
      <Column field="nombre_instalador" header="Instalador" />
      <Column field="observaciones" header="Observaciones" />
    </DataTable>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import axios from 'axios';

const reportes = ref([]);
const loading = ref(false);

async function cargarReportes() {
  loading.value = true;
  try {
    // Ajusta el endpoint si es necesario
    const res = await axios.get('https://64.227.15.111/reportes-servicio-todos');
    reportes.value = res.data;
  } catch (e) {
    reportes.value = [];
  }
  loading.value = false;
}

onMounted(cargarReportes);
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