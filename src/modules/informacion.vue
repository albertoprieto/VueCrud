<template>
  <div class="informacion">
    <h1>Panel de Inicio</h1>
    <div class="grid-container">
      <p><strong>IMEIs Registrados:</strong> {{ imeisCount ?? 0 }}</p>
      <p><strong>Cotizaciones Pendientes:</strong> {{ pendingQuotations ?? 0 }}</p>
      <p><strong>Eventos Agendados:</strong> {{ scheduledEvents ?? 0 }}</p>
      <p><strong>Reportes Generados:</strong> {{ reportsCount ?? 0 }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Card from 'primevue/card';
import { useRouter } from 'vue-router';
import { getIMEIs } from '@/services/imeiService';
import { getQuotations } from '@/services/quotationService';
import { getEventos } from '@/services/eventosService';
import { getReportesByEvento } from '@/services/reportesService';

const router = useRouter();

const imeisCount = ref(0);
const pendingQuotations = ref(0);
const scheduledEvents = ref(0);
const reportsCount = ref(0);

const loadData = async () => {
  try {
    // IMEIs
    const imeis = await getIMEIs();
    imeisCount.value = Array.isArray(imeis) ? imeis.length : 0;

    // Cotizaciones
    const quotations = await getQuotations();
    pendingQuotations.value = Array.isArray(quotations)
      ? quotations.filter(q => q.status === 'Pendiente').length
      : 0;

    // Eventos
    const eventos = await getEventos();
    scheduledEvents.value = Array.isArray(eventos)
      ? eventos.filter(e => e.status === 'Agendado').length
      : 0;

    // Reportes (sumar todos los reportes de todos los eventos)
    let totalReportes = 0;
    if (Array.isArray(eventos)) {
      for (const evento of eventos) {
        const reportes = await getReportesByEvento(evento.id);
        if (Array.isArray(reportes)) {
          totalReportes += reportes.length;
        }
      }
    }
    reportsCount.value = totalReportes;
  } catch (error) {
    imeisCount.value = 0;
    pendingQuotations.value = 0;
    scheduledEvents.value = 0;
    reportsCount.value = 0;
    // Puedes mostrar un mensaje de error si lo deseas
    // console.error('Error cargando datos:', error);
  }
};

onMounted(loadData);
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
  background-color: #3f3f3f;
  /* Gris muy oscuro */
  color: #e4c8c8;
  /* Texto blanco para contraste */
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  padding: 20px;
  border-radius: 8px;
  /* Bordes redondeados */
}

.card:hover {
  transform: translateY(-10px);
  box-shadow: 0 10px 20px rgba(8, 74, 255, 0.2);
}

.card h2 {
  color: #e4c8c8;
  /* Asegura que los títulos sean visibles */
}

.card p {
  color: #e4c8c8;
  /* Texto secundario en gris claro */
}
</style>