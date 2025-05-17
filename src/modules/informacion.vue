<template>
  <div class="informacion">
    <h1>Panel de Inicio</h1>
    <div class="grid-container">
      <!-- Resumen de Datos -->
      <Card class="card card-summary">
        <template #title>
          <h2>Resumen</h2>
        </template>
        <p><strong>IMEIs Registrados:</strong> {{ imeisCount }}</p>
        <p><strong>Cotizaciones Pendientes:</strong> {{ pendingQuotations }}</p>
        <p><strong>Eventos Agendados:</strong> {{ scheduledEvents }}</p>
        <p><strong>Reportes Generados:</strong> {{ reportsCount }}</p>
      </Card>

      <!-- Accesos Rápidos -->
      <Card class="card card-access" @click="navigateTo('/registrar')">
        <template #title>
          <h2>Registrar IMEI</h2>
        </template>
        <p>Acceso rápido para registrar nuevos IMEIs en el inventario.</p>
      </Card>

      <Card class="card card-access" @click="navigateTo('/consultar-cotizaciones')">
        <template #title>
          <h2>Consultar Cotizaciones</h2>
        </template>
        <p>Consulta y gestiona las cotizaciones existentes.</p>
      </Card>

      <Card class="card card-access" @click="navigateTo('/calendario-cotizaciones')">
        <template #title>
          <h2>Calendario</h2>
        </template>
        <p>Visualiza y gestiona los eventos agendados.</p>
      </Card>

      <Card class="card card-access" @click="navigateTo('/consultar-reportes')">
        <template #title>
          <h2>Consultar Reportes</h2>
        </template>
        <p>Consulta los reportes generados de servicios realizados.</p>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import Card from 'primevue/card';
import { useRouter } from 'vue-router';
import { useItemsStore } from '@/stores/itemStore';
import { useQuotationStore } from '@/stores/quotationStore';
import { useEventosStore } from '@/stores/eventosStore';
import { useReportesStore } from '@/stores/reportesStore';

const router = useRouter();
const itemsStore = useItemsStore();
const quotationStore = useQuotationStore();
const eventosStore = useEventosStore();
const reportesStore = useReportesStore();

// Resumen de datos
const imeisCount = computed(() => itemsStore.items.length);
const pendingQuotations = computed(() => quotationStore.getQuotations().filter(q => q.status === 'Pendiente').length);
const scheduledEvents = computed(() => eventosStore.getEventos().filter(e => e.status === 'Agendado').length);
const reportsCount = computed(() => reportesStore.getReportes().length);

const navigateTo = (route) => {
  router.push(route);
};

onMounted(() => {
  console.log('Componente Información montado');
});
</script>

<style scoped>
.informacion {
  text-align: center;
  margin: 20px;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.card {
  background-color: #3f3f3f; /* Gris muy oscuro */
  color: #e4c8c8; /* Texto blanco para contraste */
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  padding: 20px;
  border-radius: 8px; /* Bordes redondeados */
}

.card:hover {
  transform: translateY(-10px);
  box-shadow: 0 10px 20px rgba(8, 74, 255, 0.2);
}

.card h2 {
  color: #e4c8c8; /* Asegura que los títulos sean visibles */
}

.card p {
  color: #e4c8c8; /* Texto secundario en gris claro */
}
</style>